"""
Field normalization utilities for data cleaning.
"""

from __future__ import annotations

import re
from typing import Any, Optional, Tuple, Tuple
import hashlib
import random

# Units we support (extend if needed)
_ALLOWED_UNITS = ("GR", "KG", "ML", "L")


def to_int(value: Any) -> Optional[int]:
    """Convert various representations to int.

    Handles:
    - '16 pcs' → 16
    - '1.000' → 1000
    - 16.0 → 16
    - None → None

    Returns None if conversion is not possible.
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    s = str(value).strip()
    if not s:
        return None

    digits = re.findall(r"\d+", s)
    if not digits:
        return None

    return int("".join(digits))


def to_float(value: Any) -> Optional[float]:
    """Convert various representations to float.

    Handles:
    - '1,50' → 1.5
    - '1.50' → 1.5
    - None → None

    Returns None if conversion is not possible.
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    if not s:
        return None

    try:
        return float(s.replace(",", "."))
    except (ValueError, AttributeError):
        return None


def _normalize_number_str(num_str: str) -> str:
    """
    Normalize numeric string:
    - Accept "1,5" or "1.5" -> "1.5"
    - Remove trailing ".0" if it's an integer: "40.0" -> "40"
    """
    s = num_str.strip().replace(",", ".")
    try:
        f = float(s)
    except Exception:
        return num_str.strip()

    # drop .0 if integer
    if abs(f - int(f)) < 1e-12:
        return str(int(f))
    # keep as minimal string (no scientific)
    out = f"{f}"
    return out


def normalize_content(value: Any) -> Optional[str]:
    """
    Normalize content to: "<NUMBER> <UNIT>" with ONE SPACE, unit uppercase.

    NEW RULES:
    - G, g, gr, Gr, GR → GR
    - K, k, kg, Kg, KG → KG
    - ml, ML, Ml, mL → ML
    - l, L → L
    - Format: ALWAYS "<NUMBER> <UNIT>" with exactly ONE space

    Examples:
    - '110G'       → '110 GR'
    - '110g'       → '110 GR'
    - '500 gr'     → '500 GR'
    - '500GR'      → '500 GR'
    - '1.5 L'      → '1.5 L'
    - '1,5l'       → '1.5 L'
    - '750ml'      → '750 ML'
    - '40 g'       → '40 GR'
    - '1.5kg'      → '1.5 KG'
    - '2K'         → '2 KG'
    """
    if value is None:
        return None

    s = str(value).strip()
    if not s:
        return None

    # First uppercase for easier matching
    up = s.upper().strip()

    # Map common unit variants BEFORE regex extraction
    # Handle single letter units that need word boundaries
    up = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*G\b", r"\1 GR", up)  # "110G" -> "110 GR"
    up = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*K\b", r"\1 KG", up)  # "2K" -> "2 KG"
    
    # Handle multi-letter variants
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*GRAM\b", r"\1 GR", up)
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*GRAMS\b", r"\1 GR", up)
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*GR\b", r"\1 GR", up)  # normalize spacing
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*KG\b", r"\1 KG", up)  # normalize spacing
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*ML\b", r"\1 ML", up)  # normalize spacing
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*LTR\b", r"\1 L", up)
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*LITRE\b", r"\1 L", up)
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*LITER\b", r"\1 L", up)
    up = re.sub(r"(\d+(?:[.,]\d+)?)\s*L\b", r"\1 L", up)  # normalize spacing

    # Now extract the normalized pattern: number + space + unit
    m = re.search(r"(\d+(?:[.,]\d+)?)\s+([A-Z]+)\b", up)
    if not m:
        # Fallback: try without space requirement
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*([A-Z]+)\b", up)
        if not m:
            return up  # return as-is if no match

    num_raw = m.group(1)
    unit = m.group(2)

    # Normalize the number
    num = _normalize_number_str(num_raw)
    
    # Final unit validation
    if unit not in _ALLOWED_UNITS:
        # Try one more mapping
        if unit in ("G", "GRAM", "GRAMS"):
            unit = "GR"
        elif unit in ("K", "KILO", "KILOS"):
            unit = "KG"
        elif unit in ("LTR", "LITRE", "LITER"):
            unit = "L"
    
    # Return with exactly one space
    return f"{num} {unit}"


def extract_ca_cse(value: Any) -> Optional[int]:
    """
    Extract piece per case from CA/CSE notation.
    
    Examples:
    - '10CA' → 10
    - '12CSE' → 12
    - '24CA' → 24
    - 'CA10' → 10
    - 'CSE12' → 12
    
    Returns None if no CA/CSE pattern found.
    """
    if value is None:
        return None
    
    s = str(value).strip().upper()
    if not s:
        return None
    
    # Pattern 1: number followed by CA/CSE (e.g., "10CA", "12CSE")
    m = re.search(r"(\d+)\s*(CA|CSE)\b", s)
    if m:
        return int(m.group(1))
    
    # Pattern 2: CA/CSE followed by number (e.g., "CA10", "CSE12")
    m = re.search(r"\b(CA|CSE)\s*(\d+)", s)
    if m:
        return int(m.group(2))
    
    return None


def extract_content_from_description(description: Optional[str]) -> Optional[str]:
    """
    Extract content from description and return canonical "<NUMBER> <UNIT>".

    Looks for:
    - 187GR, 500GR, 1.5KG
    - 330ML, 750ML, 1.5L, 2L
    - Also supports "40 G" -> "40 GR", "110G" -> "110 GR"

    Examples:
    - "LU PRINCE 187GR MILK" → "187 GR"
    - "COCA COLA 330ML ZERO" → "330 ML"
    - "WATER 1.5L" → "1.5 L"
    - "MKA 110G TYM CHOCO" → "110 GR"
    """
    if not description:
        return None

    text = description.upper()

    # Extended pattern to catch G, K variations
    # First try with GR, KG, ML, L
    pattern = r"\b(\d+(?:[.,]\d+)?)\s*(GR|KG|ML|L|G|K)\b"
    match = re.search(pattern, text)
    if not match:
        return None

    num_raw = match.group(1)
    unit = match.group(2)

    # Convert single-letter units
    if unit == "G":
        unit = "GR"
    elif unit == "K":
        unit = "KG"

    num = _normalize_number_str(num_raw)
    return f"{num} {unit}"


def clean_description_from_content(description: Optional[str], content: Optional[str]) -> Optional[str]:
    """Remove content information AND CA/CSE notation from product description.

    Examples:
        ("LU PRINCE 187GR MILK", "187 GR") → "LU PRINCE MILK"
        ("COCA COLA 330ML ZERO", "330 ML") → "COCA COLA ZERO"
        ("MKA 110G TYM CHOCO 10CA", "110 GR") → "MKA TYM CHOCO"
    """
    if not description:
        return description

    desc = description.strip()

    # Step 1: Remove content if provided
    if content:
        # content can be "187 GR" but description might contain "187GR" or "187G"
        m = re.match(r"^\s*(\d+(?:[.,]\d+)?)\s*([A-Z]+)\s*$", content.strip().upper())
        if m:
            num = m.group(1).replace(",", ".")
            unit = m.group(2)
            
            # Build flexible pattern to match variations:
            # 187GR, 187 GR, 187G, 187 G, etc.
            # If unit is "GR", also match "G"
            if unit == "GR":
                pattern = rf"\b{re.escape(num)}\s*(?:GR|G)\b"
            elif unit == "KG":
                pattern = rf"\b{re.escape(num)}\s*(?:KG|K)\b"
            else:
                pattern = rf"\b{re.escape(num)}\s*{re.escape(unit)}\b"
            
            desc = re.sub(pattern, " ", desc, flags=re.IGNORECASE)
        else:
            # fallback exact remove
            pattern = r"\s*" + re.escape(content) + r"\s*"
            desc = re.sub(pattern, " ", desc, flags=re.IGNORECASE)

    # Step 2: Remove CA/CSE notation (e.g., "10CA", "12CSE", "CA10", "CSE12")
    desc = re.sub(r"\b\d+\s*(?:CA|CSE)\b", " ", desc, flags=re.IGNORECASE)
    desc = re.sub(r"\b(?:CA|CSE)\s*\d+\b", " ", desc, flags=re.IGNORECASE)

    # Step 3: Clean up multiple spaces
    desc = re.sub(r"\s+", " ", desc).strip()
    
    return desc if desc else description


def force_clean_description(description: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    FORCE clean description from ANY content pattern, regardless of content field.
    
    This is used as post-processing after LLM extraction to ensure descriptions
    are always clean, even if LLM failed to properly separate content.
    
    Returns:
        tuple: (cleaned_description, extracted_content)
        - If content found: returns cleaned description and the content
        - If no content found: returns original description and None
    
    Examples:
        "MILKA 120G COW" → ("MILKA COW", "120 GR")
        "OREO 154G BROWNIE" → ("OREO BROWNIE", "154 GR")
        "TUC ORIGINAL" → ("TUC ORIGINAL", None)
        "MKA 110G CHOCO 10CA" → ("MKA CHOCO", "110 GR")
    """
    if not description:
        return description, None
    
    desc = description.strip()
    
    # Try to extract content from description
    extracted_content = extract_content_from_description(desc)
    
    if not extracted_content:
        # No content found, return as-is
        return desc, None
    
    # Clean the description by removing content
    cleaned = clean_description_from_content(desc, extracted_content)
    
    return cleaned, extracted_content


def normalize_languages(value: Any) -> Optional[str]:
    """
    Normalize languages:
    - Separator: "/" (NO spaces) => "NL/FR/DE"
    - Uppercase tokens
    - Shuffle order (deterministic per input so it doesn't change every run)
    """
    if value is None:
        return None

    s = str(value).strip()
    if not s:
        return None

    up = s.upper()

    # Split on common separators: comma, semicolon, slash, pipe, backslash, multiple spaces
    parts = re.split(r"\s*[,;/|\\]\s*|\s{2,}", up)
    parts = [p.strip() for p in parts if p and p.strip()]
    if not parts:
        return None

    # Remove duplicates while preserving order
    seen = set()
    uniq = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            uniq.append(p)

    if not uniq:
        return None
    if len(uniq) == 1:
        return uniq[0]

    # Deterministic shuffle: same input -> same shuffled output
    seed_src = "/".join(uniq).encode("utf-8")
    seed = int(hashlib.md5(seed_src).hexdigest(), 16)
    rng = random.Random(seed)
    rng.shuffle(uniq)

    return "/".join(uniq)
