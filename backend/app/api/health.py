from __future__ import annotations

from typing import Any

import httpx
import redis
from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.db import get_engine
from app.llm import get_llm_client

router = APIRouter(tags=["health"])


def _check_db() -> dict[str, Any]:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("select 1"))
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc).splitlines()[0]}


def _check_redis() -> dict[str, Any]:
    try:
        redis.Redis.from_url(get_settings().redis_url, socket_timeout=2).ping()
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _check_grobid() -> dict[str, Any]:
    try:
        resp = httpx.get(f"{get_settings().grobid_url}/api/isalive", timeout=2)
        return {"ok": resp.status_code == 200}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@router.get("/api/health")
def health() -> dict[str, Any]:
    """Liveness of every dependency plus LLM provider state. Never raises."""
    services = {"database": _check_db(), "redis": _check_redis(), "grobid": _check_grobid()}
    return {
        "status": "ok" if all(s["ok"] for s in services.values()) else "degraded",
        "services": services,
        "llm": get_llm_client().status(),
    }
