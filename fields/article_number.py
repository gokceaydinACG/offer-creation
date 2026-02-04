"""Article number generation with persistent state.

Generates unique article numbers in format: AC00001000
- Prefix: AC
- Width: 8 digits
- Sequential counter stored in data/article_number.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class ArticleNumberConfig:
    """Configuration for article number format."""
    prefix: str = "AC"
    width: int = 8          # numeric part width (e.g. 00001000 -> 8 digits)
    start_next: int = 1000  # used only if state file doesn't exist


class ArticleNumberError(RuntimeError):
    """Custom exception for article number operations."""
    pass


def _project_root() -> Path:
    """Get project root directory.
    
    Structure: offer_creation/fields/article_number.py
    parents[1] = offer_creation
    """
    return Path(__file__).resolve().parents[1]


def _state_path() -> Path:
    """Get path to article number state file."""
    return _project_root() / "data" / "article_number.json"


def _load_state(state_path: Path, cfg: ArticleNumberConfig) -> int:
    """Load next article number from state file.
    
    Returns the next integer to allocate.
    If state file doesn't exist, returns cfg.start_next.
    """
    if not state_path.exists():
        return cfg.start_next

    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ArticleNumberError(f"Failed to read/parse state file: {state_path}") from e

    if not isinstance(raw, dict) or "next" not in raw:
        raise ArticleNumberError(
            f"Invalid state format in {state_path}. Expected {{\"next\": <int>}}"
        )

    nxt = raw["next"]
    if not isinstance(nxt, int) or nxt < 0:
        raise ArticleNumberError(f"Invalid 'next' value in {state_path}: {nxt}")

    return nxt


def _save_state(state_path: Path, next_value: int) -> None:
    """Save next article number to state file atomically."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(".tmp")

    payload = {"next": next_value}
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    tmp_path.replace(state_path)  # atomic on same filesystem


def format_article_number(n: int, cfg: ArticleNumberConfig = ArticleNumberConfig()) -> str:
    """Format integer as article number string.
    
    Example:
        format_article_number(1000) -> "AC00001000"
    """
    if n < 0:
        raise ArticleNumberError(f"Cannot format negative article number: {n}")
    return f"{cfg.prefix}{n:0{cfg.width}d}"


def allocate(count: int, cfg: ArticleNumberConfig = ArticleNumberConfig()) -> List[str]:
    """Allocate sequential article numbers and persist counter.
    
    Example:
        allocate(3) -> ["AC00001000", "AC00001001", "AC00001002"]
    
    Args:
        count: Number of article numbers to allocate
        cfg: Configuration for article number format
        
    Returns:
        List of allocated article numbers
        
    Raises:
        ArticleNumberError: If count is invalid or state file is corrupted
    """
    if not isinstance(count, int) or count <= 0:
        raise ArticleNumberError(f"count must be a positive integer, got: {count}")

    state_path = _state_path()
    current_next = _load_state(state_path, cfg)

    # Generate sequential numbers
    allocated_ints = list(range(current_next, current_next + count))
    allocated = [format_article_number(n, cfg) for n in allocated_ints]

    # Persist new state
    new_next = current_next + count
    _save_state(state_path, new_next)

    return allocated


def peek_next(cfg: ArticleNumberConfig = ArticleNumberConfig()) -> str:
    """Get next article number without incrementing counter.
    
    Useful for previewing what the next allocation would be.
    
    Example:
        peek_next() -> "AC00001005"
    """
    state_path = _state_path()
    current_next = _load_state(state_path, cfg)
    return format_article_number(current_next, cfg)


def reset(start_value: int = 1000, cfg: ArticleNumberConfig = ArticleNumberConfig()) -> None:
    """Reset article number counter to a specific value.
    
    ⚠️  WARNING: Use with caution! Only for testing or migration.
    
    Args:
        start_value: The next article number to allocate
        cfg: Configuration for article number format
    """
    if start_value < 0:
        raise ArticleNumberError(f"start_value must be non-negative, got: {start_value}")
    
    state_path = _state_path()
    _save_state(state_path, start_value)