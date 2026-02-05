"""Convert any input format to Canonical using LLM extraction."""

from __future__ import annotations

import json
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List

from domain.canonical import CanonicalRow
from input_readers import read_excel, read_image_as_data_url, read_pdf

from .llm_client import get_client
from .prompts import EXTRACTION_SYSTEM_PROMPT, build_extraction_prompt
from .chunked_processor import process_excel_in_chunks
from fields.normalization import to_float, to_int


def _extract_content_from_text(text: str) -> str | None:
    """Extract content pattern from any text.
    
    Examples: 187GR, 500GR, 1.5KG, 330ML, 2L
    """
    if not text:
        return None
    
    pattern = r'\b(\d+(?:[.,]\d+)?)\s*(GR|KG|ML|L)\b'
    match = re.search(pattern, text.upper())
    
    if match:
        number = match.group(1).replace(',', '.')
        unit = match.group(2)
        return f"{number}{unit}"
    
    return None


def _pre_extract_content_from_rows(rows: List[Dict]) -> List[str | None]:
    """Pre-extract content from raw rows BEFORE LLM.
    
    Returns list of content values (or None) matching row order.
    """
    extracted = []
    
    for row in rows:
        content = None
        # Look through all fields for content pattern
        for value in row.values():
            if value:
                content = _extract_content_from_text(str(value))
                if content:
                    break  # Use first match
        extracted.append(content)
    
    return extracted


def _parse_llm_response(raw_response: str) -> Dict[str, Any]:
    """Parse LLM response, handling markdown code blocks."""
    raw = raw_response.strip()
    
    # Remove markdown code blocks if present
    if raw.startswith("```"):
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, flags=re.DOTALL)
        if match:
            raw = match.group(1)
        else:
            raw = re.sub(r"```(?:json)?", "", raw).strip()
    
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        # Last resort: find first JSON object
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return valid JSON. Error: {e}\nGot: {raw[:500]}")
        return json.loads(match.group(0))


def _call_llm_extraction(raw_data: str, file_type: str, model: str = "gpt-4o-mini", extract_price: bool = False) -> List[Dict[str, Any]]:
    """Call LLM to extract structured data.
    
    Args:
        raw_data: Raw text/data from file
        file_type: 'excel', 'pdf', or 'image'
        model: LLM model to use
        extract_price: If True, extract price from supplier offer
    """
    client = get_client()
    
    user_prompt = build_extraction_prompt(raw_data, file_type, extract_price)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
    )
    
    raw_output = response.choices[0].message.content
    if not raw_output:
        raise ValueError("LLM returned empty response")
    
    parsed = _parse_llm_response(raw_output)
    
    if "products" in parsed:
        return parsed["products"]
    else:
        return [parsed]


def _dict_to_canonical(product: Dict[str, Any], source_file: str, source_row: int) -> CanonicalRow:
    """Convert extracted dict to CanonicalRow with type safety."""
    return CanonicalRow(
        ean=product.get("ean"),
        product_description=product.get("product_description"),
        content=product.get("content"),
        languages=product.get("languages"),
        piece_per_case=to_int(product.get("piece_per_case")),
        case_per_pallet=to_int(product.get("case_per_pallet")),
        pieces_per_pallet=to_int(product.get("pieces_per_pallet")),
        bbd=product.get("bbd"),
        availability_pieces=to_int(product.get("availability_pieces")),
        availability_cartons=to_int(product.get("availability_cartons")),
        availability_pallets=to_int(product.get("availability_pallets")),
        price_unit_eur=to_float(product.get("price_unit_eur")),
        source_file=source_file,
        source_row=source_row,
    )


def excel_to_canonical(xlsx_path: Path, model: str = "gpt-4o-mini", extract_price: bool = False) -> List[CanonicalRow]:
    """Convert Excel file to Canonical using LLM extraction.
    
    Uses chunked processing for large files (>50 rows) to avoid token limits.
    Pre-extracts content from raw data before LLM processing as safety net.
    
    Args:
        xlsx_path: Path to Excel file
        model: LLM model to use
        extract_price: If True, extract price from supplier offer
    """
    # Read raw Excel data
    rows = read_excel(xlsx_path)
    
    # PRE-EXTRACT content before LLM (safety net)
    pre_extracted_content = _pre_extract_content_from_rows(rows)
    
    # Process with chunking (handles datetime sanitization internally)
    products = process_excel_in_chunks(rows, model, extract_price)
    
    # Convert to Canonical
    canonical_rows = [
        _dict_to_canonical(p, str(xlsx_path), idx)
        for idx, p in enumerate(products, start=1)
    ]
    
    # POST-FILL: If LLM missed content, use pre-extracted
    for i, row in enumerate(canonical_rows):
        if not row.get("content") and i < len(pre_extracted_content):
            if pre_extracted_content[i]:
                row["content"] = pre_extracted_content[i]
    
    return canonical_rows


def pdf_to_canonical(pdf_path: Path, model: str = "gpt-4o-mini", extract_price: bool = False) -> List[CanonicalRow]:
    """Convert PDF file to Canonical using LLM extraction.
    
    Args:
        pdf_path: Path to PDF file
        model: LLM model to use
        extract_price: If True, extract price from supplier offer
    """
    raw_text = read_pdf(pdf_path)
    products = _call_llm_extraction(raw_text, "pdf", model, extract_price)
    
    return [
        _dict_to_canonical(p, str(pdf_path), idx)
        for idx, p in enumerate(products, start=1)
    ]


def image_to_canonical(image_path: Path, model: str = "gpt-4o-mini", extract_price: bool = False) -> List[CanonicalRow]:
    """Convert image file to Canonical using LLM vision extraction.
    
    Args:
        image_path: Path to image file
        model: LLM model to use
        extract_price: If True, extract price from supplier offer
    """
    data_url = read_image_as_data_url(image_path)
    
    client = get_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": EXTRACTION_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": build_extraction_prompt("See image below", "image", extract_price)
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    }
                ]
            }
        ],
        temperature=0,
    )
    
    raw_output = response.choices[0].message.content
    if not raw_output:
        raise ValueError("LLM returned empty response")
    
    parsed = _parse_llm_response(raw_output)
    products = parsed.get("products", [parsed]) if isinstance(parsed, dict) else [parsed]
    
    return [
        _dict_to_canonical(p, str(image_path), idx)
        for idx, p in enumerate(products, start=1)
    ]