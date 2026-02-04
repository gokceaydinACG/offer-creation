from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class ArticleNumberConfig:
    prefix: str = "AC"
    width: int = 8          # numeric part width (e.g. 00001000 -> 8 digits)
    start_next: int = 1000  # used only if the state file doesn't exist / is invalid


class ArticleNumberError(RuntimeError):
    pass


def _project_root() -> Path:
    # .../offer_creation/src/fields/article_number/logic.py -> parents[3] == offer_creation
    return Path(__file__).resolve().parents[3]


def _state_path() -> Path:
    return _project_root() / "data" / "article_number.json"


def _load_state(state_path: Path, cfg: ArticleNumberConfig) -> int:
    """
    Returns the next integer to allocate.
    """
    if not state_path.exists():
        return cfg.start_next

    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ArticleNumberError(f"Failed to read/parse state file: {state_path}") from e

    if not isinstance(raw, dict) or "next" not in raw:
        raise ArticleNumberError(f"Invalid state format in {state_path}. Expected {{\"next\": <int>}}")

    nxt = raw["next"]
    if not isinstance(nxt, int) or nxt < 0:
        raise ArticleNumberError(f"Invalid 'next' value in {state_path}: {nxt}")

    return nxt


def _save_state(state_path: Path, next_value: int) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(".tmp")

    payload = {"next": next_value}
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(state_path)  # atomic-ish on same filesystem


def format_article_number(n: int, cfg: ArticleNumberConfig = ArticleNumberConfig()) -> str:
    """
    Formats integer n as AC00001000 style string.
    """
    if n < 0:
        raise ArticleNumberError(f"Cannot format negative article number: {n}")
    return f"{cfg.prefix}{n:0{cfg.width}d}"


def allocate(count: int, cfg: ArticleNumberConfig = ArticleNumberConfig()) -> List[str]:
    """
    Allocates `count` sequential article numbers and persists the updated counter.
    Example: allocate(3) -> ["AC00001000", "AC00001001", "AC00001002"]
    """
    if not isinstance(count, int) or count <= 0:
        raise ArticleNumberError(f"count must be a positive integer, got: {count}")

    state_path = _state_path()
    current_next = _load_state(state_path, cfg)

    allocated_ints = list(range(current_next, current_next + count))
    allocated = [format_article_number(n, cfg) for n in allocated_ints]

    new_next = current_next + count
    _save_state(state_path, new_next)

    return allocated


def peek_next(cfg: ArticleNumberConfig = ArticleNumberConfig()) -> str:
    """
    Returns the next article number that would be allocated, without incrementing.
    """
    state_path = _state_path()
    current_next = _load_state(state_path, cfg)
    return format_article_number(current_next, cfg)
