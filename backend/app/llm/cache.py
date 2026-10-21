"""LLM response cache. Re-running a paper with the same inputs costs zero calls."""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from typing import Any, Protocol

from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models.llm_cache import LLMCacheEntry


@dataclass(frozen=True)
class CachedResponse:
    provider: str
    model: str
    prompt_version: str
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


def make_cache_key(
    *,
    provider: str,
    model: str,
    prompt: str,
    system: str | None,
    json_schema: dict[str, Any] | None,
    prompt_version: str,
    thinking: bool,
    temperature: float,
    cache_version: int,
) -> str:
    """sha256 over every input that can change the output.

    The prompt already contains the paper text, so the paper's identity is part of the key.
    """
    payload = {
        "v": cache_version,
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "system": system,
        "schema": json_schema,
        "prompt_version": prompt_version,
        "thinking": thinking,
        "temperature": temperature,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()


class LLMCache(Protocol):
    def get(self, key: str) -> CachedResponse | None: ...

    def set(self, key: str, value: CachedResponse) -> None: ...


class MemoryCache:
    """Process-local cache for tests and DB-less scripts."""

    def __init__(self) -> None:
        self._data: dict[str, CachedResponse] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> CachedResponse | None:
        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value: CachedResponse) -> None:
        with self._lock:
            self._data[key] = value

    def __len__(self) -> int:
        return len(self._data)


class SqlCache:
    """Cache in the llm_cache table (Postgres in compose, SQLite works too)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get(self, key: str) -> CachedResponse | None:
        with Session(self._engine) as session:
            row = session.get(LLMCacheEntry, key)
            if row is None:
                return None
            return CachedResponse(
                provider=row.provider,
                model=row.model,
                prompt_version=row.prompt_version,
                text=row.response,
                input_tokens=row.input_tokens,
                output_tokens=row.output_tokens,
            )

    def set(self, key: str, value: CachedResponse) -> None:
        values = {
            "key": key,
            "provider": value.provider,
            "model": value.model,
            "prompt_version": value.prompt_version,
            "response": value.text,
            "input_tokens": value.input_tokens,
            "output_tokens": value.output_tokens,
        }
        insert = pg_insert if self._engine.dialect.name == "postgresql" else sqlite_insert
        # Two workers can finish the same call; first write wins, both are identical anyway.
        stmt = insert(LLMCacheEntry).values(**values).on_conflict_do_nothing(index_elements=["key"])
        with Session(self._engine) as session, session.begin():
            session.execute(stmt)
