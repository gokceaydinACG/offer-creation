"""Configuration package - exports all settings."""

from .settings import (
    # Paths
    PROJECT_ROOT,
    INPUT_ROOT,
    OUTPUT_ROOT,
    FOOD_INPUT_DIR,
    HPC_INPUT_DIR,
    MOVE_INPUT_TO_PROCESSED,
    
    # File limits
    MAX_FILE_SIZE_MB,
    MAX_SHEET_ROWS,
    MAX_SHEET_COLS,
    MAX_SHEETS,
    EXTREME_COLS_LIMIT,
    
    # LLM limits
    MAX_TEXT_CHARS_BEFORE_LLM,
    JSON_RETRY_ATTEMPTS,
    CHUNK_SIZE,
    
    # LLM settings
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
)

__all__ = [
    # Paths
    "PROJECT_ROOT",
    "INPUT_ROOT",
    "OUTPUT_ROOT",
    "FOOD_INPUT_DIR",
    "HPC_INPUT_DIR",
    "MOVE_INPUT_TO_PROCESSED",
    
    # File limits
    "MAX_FILE_SIZE_MB",
    "MAX_SHEET_ROWS",
    "MAX_SHEET_COLS",
    "MAX_SHEETS",
    "EXTREME_COLS_LIMIT",
    
    # LLM limits
    "MAX_TEXT_CHARS_BEFORE_LLM",
    "JSON_RETRY_ATTEMPTS",
    "CHUNK_SIZE",
    
    # LLM settings
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
]