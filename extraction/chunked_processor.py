"""Chunked processing for large Excel files.

Splits large Excel files into smaller chunks to avoid LLM token limits
and JSON parsing errors. Each chunk is processed independently and results
are merged.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .llm_client import get_client
from .prompts import EXTRACTION_SYSTEM_PROMPT, build_extraction_prompt


CHUNK_SIZE = 50  # Rows per chunk


def _sanitize_for_json(obj: Any) -> Any:
    """Convert non-JSON-serializable objects to JSON-safe types.
    
    Handles datetime, date, and other problematic types from Excel.
    """
    from datetime import datetime, date
    
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    else:
        return obj


def _parse_llm_response(raw_response: str) -> Dict[str, Any]:
    """Parse LLM response, handling markdown code blocks."""
    import re
    
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


def _call_llm_extraction_for_chunk(
    chunk_data: str,
    model: str = "gpt-4o-mini",
    extract_price: bool = False
) -> List[Dict[str, Any]]:
    """Call LLM to extract structured data for a single chunk.
    
    Args:
        chunk_data: JSON string of Excel rows
        model: LLM model to use
        extract_price: If True, extract price from supplier offer
    """
    client = get_client()
    
    user_prompt = build_extraction_prompt(chunk_data, "excel", extract_price)
    
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


def process_excel_in_chunks(
    rows: List[Dict],
    model: str = "gpt-4o-mini",
    extract_price: bool = False,
    chunk_size: int = CHUNK_SIZE
) -> List[Dict[str, Any]]:
    """Process large Excel files in chunks to avoid token limits.
    
    Args:
        rows: Raw Excel rows (from read_excel)
        model: LLM model to use
        extract_price: If True, extract price from supplier offer
        chunk_size: Number of rows per chunk (default: 50)
        
    Returns:
        List of extracted products (merged from all chunks)
    """
    total_rows = len(rows)
    
    if total_rows == 0:
        return []
    
    # If small enough, process in one go
    if total_rows <= chunk_size:
        sanitized = _sanitize_for_json(rows)
        raw_data = json.dumps(sanitized, indent=2, ensure_ascii=False)
        return _call_llm_extraction_for_chunk(raw_data, model, extract_price)
    
    # Process in chunks
    all_products = []
    num_chunks = (total_rows + chunk_size - 1) // chunk_size  # Ceiling division
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, total_rows)
        
        chunk = rows[start_idx:end_idx]
        
        # Sanitize and convert to JSON
        sanitized_chunk = _sanitize_for_json(chunk)
        chunk_data = json.dumps(sanitized_chunk, indent=2, ensure_ascii=False)
        
        # Process chunk
        chunk_products = _call_llm_extraction_for_chunk(chunk_data, model, extract_price)
        
        # Merge results
        all_products.extend(chunk_products)
    
    return all_products