"""Project configuration and paths."""

from __future__ import annotations

from pathlib import Path

# Project root: .../offer_creation
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Input / Output directories
INPUT_ROOT = PROJECT_ROOT / "input_offers"
OUTPUT_ROOT = PROJECT_ROOT / "offer_outputs"

FOOD_INPUT_DIR = INPUT_ROOT / "food"
HPC_INPUT_DIR = INPUT_ROOT / "hpc"

# DEV: Keep input files in place (don't move to processed)
MOVE_INPUT_TO_PROCESSED = False