"""Extract text from PDF files."""

from __future__ import annotations

from pathlib import Path

import pdfplumber


def read_pdf(pdf_path: Path) -> str:
    """Extract all text from PDF file.
    
    Preserves structure and formatting where possible.
    No interpretation - just raw text extraction.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text_parts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    
    return "\n\n".join(text_parts)