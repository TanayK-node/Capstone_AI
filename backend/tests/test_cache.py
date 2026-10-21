from sqlalchemy import create_engine

from app.llm.cache import CachedResponse, SqlCache, make_cache_key
from app.models import Base

BASE = dict(
    provider="gemini",
    model="flash",
    prompt="p",
    system=None,
    json_schema={"type": "object"},
    prompt_version="x@1",
    thinking=False,
    temperature=0.0,
    cache_version=1,
)


def test_key_is_deterministic_and_sensitive_to_every_input() -> None:
    key = make_cache_key(**BASE)  # type: ignore[arg-type]
    assert key == make_cache_key(**BASE)  # type: ignore[arg-type]
    for field, other in [
        ("model", "flash-lite"),
        ("prompt", "q"),
        ("prompt_version", "x@2"),
        ("json_schema", {"type": "array"}),
        ("thinking", True),
        ("cache_version", 2),
    ]:
        assert make_cache_key(**{**BASE, field: other}) != key, field  # type: ignore[arg-type]


def test_sql_cache_roundtrip_and_duplicate_write() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    cache = SqlCache(engine)
    value = CachedResponse("gemini", "flash", "x@1", '{"a": 1}', 10, 5)
    assert cache.get("k") is None
    cache.set("k", value)
    cache.set("k", value)  # second worker finishing the same call must not raise
    assert cache.get("k") == value
