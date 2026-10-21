import pytest
from fastapi.testclient import TestClient

from app.llm import get_llm_client


def test_health_reports_services_and_llm_without_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Point at a throwaway SQLite DB and unreachable redis/grobid: health must still answer.
    monkeypatch.setenv("PAPERLENS_DATABASE_URL", "sqlite://")
    monkeypatch.setenv("PAPERLENS_REDIS_URL", "redis://127.0.0.1:1/0")
    monkeypatch.setenv("PAPERLENS_GROBID_URL", "http://127.0.0.1:1")
    from app.config import get_settings
    from app.db import get_engine

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_llm_client.cache_clear()
    from app.main import create_app

    resp = TestClient(create_app()).get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["services"]["database"]["ok"] is True
    assert body["services"]["redis"]["ok"] is False
    assert body["status"] == "degraded"
    assert body["llm"]["primary"] == "gemini"
    # Gemini-only config and no key in tests: nothing is configured, and health still answers.
    assert body["llm"]["configured"] == []
    assert body["llm"]["active"] is None
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_llm_client.cache_clear()
