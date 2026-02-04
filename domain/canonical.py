from __future__ import annotations

from typing import Optional, TypedDict


class CanonicalRow(TypedDict, total=False):
    # core identifiers
    ean: Optional[str]
    product_description: Optional[str]
    content: Optional[str]
    languages: Optional[str]

    # packaging
    piece_per_case: Optional[int]
    case_per_pallet: Optional[int]
    pieces_per_pallet: Optional[int]

    # FOOD-only (HPC will keep None)
    bbd: Optional[str]

    # availability
    availability_cartons: Optional[int]
    availability_pieces: Optional[int]
    availability_pallets: Optional[int]

    # pricing
    price_unit_eur: Optional[float]

    # provenance (debug)
    source_file: Optional[str]
    source_row: Optional[int]
