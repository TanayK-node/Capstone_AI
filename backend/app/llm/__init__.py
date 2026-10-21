"""LLM gateway. Import get_llm_client() rather than building providers directly."""

from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.llm.client import LLMClient, build_client


@lru_cache
def get_llm_client() -> LLMClient:
    from app.db import get_engine
    from app.llm.cache import SqlCache

    return build_client(get_settings(), SqlCache(get_engine()))


__all__ = ["LLMClient", "build_client", "get_llm_client"]
