"""Semantic Scholar Graph API: the paper, its references and the papers citing it (M12).

Read-only metadata. Without an API key requests share a public pool that often answers 429,
so those (and 5xx) are retried with a backoff. Anything else unusable returns None / [] and
the caller falls back to the PDF's own reference list.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

log = logging.getLogger("paperlens.context")
API = "https://api.semanticscholar.org/graph/v1"
PAPER_FIELDS = (
    "title,year,venue,authors,citationCount,influentialCitationCount,referenceCount,externalIds,url"
)
REF_FIELDS = "isInfluential,title,year,venue,authors,citationCount,abstract,externalIds,url"
CITE_FIELDS = "isInfluential,title,year,venue,authors,citationCount,externalIds,url"


class S2Error(Exception):
    pass


class S2Client:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout_s: float = 20.0,
        retries: int = 5,
        min_interval_s: float = 1.1,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        headers = {"User-Agent": "PaperLens (citation graph)"}
        if api_key:
            headers["x-api-key"] = api_key
        self._http = httpx.Client(
            base_url=API, headers=headers, timeout=timeout_s, transport=transport
        )
        self.retries = retries
        # The shared (keyless) pool allows about one request per second for everyone, so
        # requests are spaced out; with a key the limit is per key.
        self.min_interval_s = min_interval_s
        self._last = 0.0
        self._sleep = sleep

    def close(self) -> None:
        self._http.close()

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any] | None:
        """JSON body, None on 404; S2Error when the API stays unavailable."""
        for attempt in range(self.retries + 1):
            wait = self._last + self.min_interval_s - time.monotonic()
            if wait > 0:
                self._sleep(wait)
            self._last = time.monotonic()
            try:
                resp = self._http.get(path, params=params)
            except httpx.HTTPError as exc:
                if attempt == self.retries:
                    raise S2Error(f"Semantic Scholar unreachable: {exc}") from exc
                self._sleep(2.0**attempt)
                continue
            if resp.status_code == 404:
                return None
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt == self.retries:
                    raise S2Error(f"Semantic Scholar HTTP {resp.status_code} (busy; try later)")
                after = resp.headers.get("Retry-After", "")
                self._sleep(float(after) if after.isdigit() else min(30.0, 2.0 ** (attempt + 1)))
                continue
            if resp.status_code != 200:
                raise S2Error(f"Semantic Scholar HTTP {resp.status_code}")
            data: dict[str, Any] = resp.json()
            return data
        return None  # not reached

    def find(
        self, *, arxiv_id: str | None, doi: str | None, s2_id: str | None, title: str | None
    ) -> dict[str, Any] | None:
        """The paper by its ids, else by title (S2's best title match)."""
        for key in (s2_id, f"arXiv:{arxiv_id}" if arxiv_id else None,
                    f"DOI:{doi}" if doi else None):  # fmt: skip
            if key:
                data = self._get(f"/paper/{key}", {"fields": PAPER_FIELDS})
                if data:
                    return data
        if title and len(title) > 10:
            found = self._get("/paper/search/match", {"query": title, "fields": PAPER_FIELDS})
            if found and found.get("data"):
                first: dict[str, Any] = found["data"][0]
                return first
        return None

    def references(self, paper_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        """[{isInfluential, citedPaper: {...}}], in the paper's own order."""
        data = self._get(f"/paper/{paper_id}/references",
                         {"fields": REF_FIELDS, "limit": min(limit, 1000)})  # fmt: skip
        return [
            r for r in (data or {}).get("data") or [] if (r.get("citedPaper") or {}).get("title")
        ]

    def citations(self, paper_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        """[{isInfluential, citingPaper: {...}}]; S2 returns them newest first, unsorted."""
        data = self._get(f"/paper/{paper_id}/citations",
                         {"fields": CITE_FIELDS, "limit": min(limit, 1000)})  # fmt: skip
        return [
            c for c in (data or {}).get("data") or [] if (c.get("citingPaper") or {}).get("title")
        ]
