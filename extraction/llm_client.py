"""OpenAI client wrapper for LLM extraction."""

from __future__ import annotations

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Get singleton OpenAI client.
    
    OPENAI_API_KEY is read from environment variables.
    """
    global _client
    if _client is None:
        _client = OpenAI()
    return _client