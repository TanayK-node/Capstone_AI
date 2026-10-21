"""Fetch PDFs and metadata from each source (M1)."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import httpx
from lxml import etree

from app.config import Settings
from app.pipeline.ingest.resolver import ResolvedInput, SourceKind

log = logging.getLogger("paperlens.ingest")

USER_AGENT = "PaperLens/0.1 (research-paper analysis; student project)"
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
S2_FIELDS = "title,authors,year,venue,abstract,externalIds,openAccessPdf"


class FetchError(Exception):
    """Fetching failed; the message is shown to the user."""


class NoOpenAccessPdfError(FetchError):
    """Metadata found but no free PDF; the user should upload the file."""


@dataclass
class FetchedPaper:
    kind: SourceKind
    identifier: str
    pdf: bytes
    pdf_url: str
    metadata: dict[str, Any] = field(default_factory=dict)
    latex_source: bytes | None = None


class SourceFetcher:
    def __init__(self, settings: Settings, http: httpx.Client | None = None) -> None:
        self.settings = settings
        self.cfg = settings.ingest
        self.http = http or httpx.Client(
            timeout=self.cfg.download_timeout_s,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )

    # ------------------------------------------------------------ public

    def fetch(self, source: ResolvedInput) -> FetchedPaper:
        handler = {
            "arxiv": self.fetch_arxiv,
            "doi": self.fetch_doi,
            "openreview": self.fetch_openreview,
            "acl": self.fetch_acl,
            "semantic_scholar": self.fetch_semantic_scholar,
            "pdf_url": self.fetch_pdf_url,
        }.get(source.kind)
        if handler is None:
            raise FetchError(f"cannot fetch source kind {source.kind!r}")
        return handler(source.identifier)

    # ------------------------------------------------------------ helpers

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        try:
            resp = self.http.get(url, **kwargs)
        except httpx.HTTPError as exc:
            raise FetchError(f"could not reach {httpx.URL(url).host}: {exc}") from exc
        return resp

    def download_pdf(self, url: str) -> bytes:
        limit = self.cfg.max_mb * 1024 * 1024
        try:
            with self.http.stream("GET", url) as resp:
                if resp.status_code == 404:
                    raise FetchError(f"PDF not found at {url}")
                if resp.status_code >= 400:
                    raise FetchError(f"PDF download failed: HTTP {resp.status_code} from {url}")
                chunks: list[bytes] = []
                size = 0
                for chunk in resp.iter_bytes():
                    size += len(chunk)
                    if size > limit:
                        raise FetchError(f"PDF is larger than {self.cfg.max_mb} MB")
                    chunks.append(chunk)
        except httpx.HTTPError as exc:
            raise FetchError(f"PDF download failed: {exc}") from exc
        data = b"".join(chunks)
        if not data.lstrip()[:5].startswith(b"%PDF-"):
            raise FetchError(f"{url} did not return a PDF (it may be a landing page)")
        return data

    # ------------------------------------------------------------ sources

    def fetch_arxiv(self, arxiv_id: str) -> FetchedPaper:
        meta = self.arxiv_metadata(arxiv_id)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        paper = FetchedPaper("arxiv", arxiv_id, self.download_pdf(pdf_url), pdf_url, meta)
        if self.cfg.fetch_latex_source:
            paper.latex_source = self._arxiv_source(arxiv_id)
        return paper

    def arxiv_metadata(self, arxiv_id: str) -> dict[str, Any]:
        resp = self._get("https://export.arxiv.org/api/query", params={"id_list": arxiv_id})
        if resp.status_code != 200:
            log.warning("arXiv API HTTP %s for %s", resp.status_code, arxiv_id)
            return {"arxiv_id": arxiv_id}
        return parse_arxiv_atom(resp.content, arxiv_id)

    def _arxiv_source(self, arxiv_id: str) -> bytes | None:
        """The e-print tarball (gzip). Not every paper has LaTeX source; failures are fine."""
        try:
            resp = self.http.get(f"https://arxiv.org/e-print/{arxiv_id}")
        except httpx.HTTPError:
            return None
        ctype = resp.headers.get("content-type", "")
        if resp.status_code != 200 or "pdf" in ctype or len(resp.content) > 30 * 1024 * 1024:
            return None
        return resp.content

    def fetch_doi(self, doi: str) -> FetchedPaper:
        meta: dict[str, Any] = {"doi": doi}
        resp = self._get(f"https://api.crossref.org/works/{doi}")
        if resp.status_code == 200:
            meta.update(parse_crossref(resp.json().get("message", {})))
        elif resp.status_code == 404:
            raise FetchError(f"DOI {doi} not found")

        candidates: list[str] = []
        if self.cfg.contact_email:
            up = self._get(
                f"https://api.unpaywall.org/v2/{doi}", params={"email": self.cfg.contact_email}
            )
            if up.status_code == 200:
                best = up.json().get("best_oa_location") or {}
                if best.get("url_for_pdf"):
                    candidates.append(best["url_for_pdf"])
        s2 = self._s2(f"DOI:{doi}")
        if s2:
            if arxiv := (s2.get("externalIds") or {}).get("ArXiv"):
                paper = self.fetch_arxiv(arxiv)
                paper.metadata = {**paper.metadata, **meta}
                return paper
            if url := (s2.get("openAccessPdf") or {}).get("url"):
                candidates.append(url)
        for url in candidates:
            try:
                return FetchedPaper("doi", doi, self.download_pdf(url), url, meta)
            except FetchError as exc:
                log.info("open-access candidate failed: %s", exc)
        raise NoOpenAccessPdfError(
            f"no open-access PDF found for DOI {doi}; please upload the PDF instead"
        )

    def fetch_openreview(self, note_id: str) -> FetchedPaper:
        url = f"https://openreview.net/pdf?id={note_id}"
        return FetchedPaper("openreview", note_id, self.download_pdf(url), url, {})

    def fetch_acl(self, acl_id: str) -> FetchedPaper:
        url = f"https://aclanthology.org/{acl_id}.pdf"
        return FetchedPaper("acl", acl_id, self.download_pdf(url), url, {"acl_id": acl_id})

    def fetch_semantic_scholar(self, s2_id: str) -> FetchedPaper:
        data = self._s2(s2_id)
        if data is None:
            raise FetchError(f"Semantic Scholar paper {s2_id} not found")
        meta = parse_s2(data)
        if arxiv := (data.get("externalIds") or {}).get("ArXiv"):
            paper = self.fetch_arxiv(arxiv)
            paper.metadata = {**meta, **paper.metadata}
            return paper
        url = (data.get("openAccessPdf") or {}).get("url")
        if not url:
            raise NoOpenAccessPdfError(
                "Semantic Scholar lists no open-access PDF; please upload the PDF instead"
            )
        return FetchedPaper("semantic_scholar", s2_id, self.download_pdf(url), url, meta)

    def fetch_pdf_url(self, url: str) -> FetchedPaper:
        return FetchedPaper("pdf_url", url, self.download_pdf(url), url, {})

    def _s2(self, paper_id: str) -> dict[str, Any] | None:
        resp = self._get(
            f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}",
            params={"fields": S2_FIELDS},
        )
        if resp.status_code != 200:
            return None
        data: dict[str, Any] = resp.json()
        return data


# ------------------------------------------------------------------ metadata parsers


def _clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse_arxiv_atom(xml: bytes, arxiv_id: str) -> dict[str, Any]:
    root = etree.fromstring(xml)
    entry = root.find("a:entry", ATOM)
    if entry is None or entry.find("a:title", ATOM) is None:
        return {"arxiv_id": arxiv_id}
    doi = entry.find("arxiv:doi", ATOM)
    journal = entry.find("arxiv:journal_ref", ATOM)
    category = entry.find("arxiv:primary_category", ATOM)
    published = _clean(entry.findtext("a:published", namespaces=ATOM))
    return {
        "arxiv_id": arxiv_id,
        "title": _clean(entry.findtext("a:title", namespaces=ATOM)),
        "abstract": _clean(entry.findtext("a:summary", namespaces=ATOM)),
        "authors": [
            _clean(a.findtext("a:name", namespaces=ATOM)) for a in entry.iterfind("a:author", ATOM)
        ],
        "year": published[:4] or None,
        "published": published or None,
        "doi": _clean(doi.text) if doi is not None else None,
        "venue": _clean(journal.text) if journal is not None else None,
        "category": category.get("term") if category is not None else None,
    }


def parse_crossref(msg: dict[str, Any]) -> dict[str, Any]:
    issued = (msg.get("issued") or {}).get("date-parts") or [[None]]
    return {
        "title": _clean((msg.get("title") or [None])[0]),
        "authors": [
            _clean(f"{a.get('given', '')} {a.get('family', '')}") for a in msg.get("author", [])
        ],
        "venue": _clean((msg.get("container-title") or [None])[0]) or None,
        "year": str(issued[0][0]) if issued[0][0] else None,
    }


def parse_s2(data: dict[str, Any]) -> dict[str, Any]:
    ext = data.get("externalIds") or {}
    return {
        "title": data.get("title"),
        "authors": [a.get("name") for a in data.get("authors") or []],
        "year": str(data["year"]) if data.get("year") else None,
        "venue": data.get("venue") or None,
        "abstract": data.get("abstract"),
        "doi": ext.get("DOI"),
        "arxiv_id": ext.get("ArXiv"),
        "s2_id": data.get("paperId"),
    }
