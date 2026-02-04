"""Field utilities and article number generation."""

from .article_number import allocate, peek_next, ArticleNumberError
from .normalization import (
    clean_description_from_content,
    extract_content_from_description,
    normalize_content,
    normalize_languages,
    to_float,
    to_int,
)
from .packaging_math import (
    apply_packaging_math, 
    complete_availability, 
    complete_packaging_triad,
    apply_double_stackable,
)

__all__ = [
    "allocate",
    "peek_next",
    "ArticleNumberError",
    "to_int",
    "to_float",
    "normalize_content",
    "normalize_languages",
    "extract_content_from_description",
    "clean_description_from_content",
    "apply_packaging_math",
    "complete_packaging_triad",
    "complete_availability",
    "apply_double_stackable",
]