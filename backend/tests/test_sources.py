"""Source fetchers with the network mocked."""

from collections.abc import Callable

import httpx
import pytest

from app.config import Settings
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import (
    FetchError,
    NoOpenAccessPdfError,
    SourceFetcher,
    parse_arxiv_atom,
)

PDF = b"%PDF-1.7\n fake but starts right"
ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <published>2017-06-12T17:57:34Z</published>
    <title>Attention Is All
      You Need</title>
    <summary>  The dominant sequence transduction models ...  </summary>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <arxiv:primary_category term="cs.CL"/>
  </entry>
</feed>"""

Handler = Callable[[httpx.Request], httpx.Response]


def fetcher(settings: Settings, handler: Handler) -> SourceFetcher:
    http = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    return SourceFetcher(settings, http=http)


def test_parse_arxiv_atom() -> None:
    meta = parse_arxiv_atom(ATOM, "1706.03762")
    assert meta["title"] == "Attention Is All You Need"
    assert meta["authors"] == ["Ashish Vaswani", "Noam Shazeer"]
    assert meta["year"] == "2017"
    assert meta["category"] == "cs.CL"


def test_fetch_arxiv_gets_metadata_pdf_and_source(settings: Settings) -> None:
    seen: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(str(req.url))
        if req.url.host == "export.arxiv.org":
            return httpx.Response(200, content=ATOM)
        if req.url.path.startswith("/pdf/"):
            return httpx.Response(200, content=PDF)
        if req.url.path.startswith("/e-print/"):
            return httpx.Response(200, content=b"\x1f\x8b gz", headers={"content-type": "gzip"})
        return httpx.Response(404)

    paper = fetcher(settings, handler).fetch(resolve("arxiv.org/abs/1706.03762"))
    assert paper.pdf == PDF
    assert paper.metadata["title"] == "Attention Is All You Need"
    assert paper.latex_source == b"\x1f\x8b gz"
    assert any("/pdf/1706.03762" in u for u in seen)


def test_doi_without_open_access_asks_for_upload(settings: Settings) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.host == "api.crossref.org":
            return httpx.Response(200, json={"message": {"title": ["Closed Paper"]}})
        return httpx.Response(404)

    with pytest.raises(NoOpenAccessPdfError, match="upload"):
        fetcher(settings, handler).fetch(resolve("10.1000/closed.123"))


def test_doi_with_arxiv_version_uses_arxiv(settings: Settings) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.host == "api.crossref.org":
            return httpx.Response(200, json={"message": {"title": ["BERT"]}})
        if req.url.host == "api.semanticscholar.org":
            return httpx.Response(200, json={"externalIds": {"ArXiv": "1810.04805"}})
        if req.url.host == "export.arxiv.org":
            return httpx.Response(200, content=ATOM)
        if req.url.path.startswith("/pdf/1810.04805"):
            return httpx.Response(200, content=PDF)
        return httpx.Response(404)

    paper = fetcher(settings, handler).fetch(resolve("10.18653/v1/N19-1423"))
    assert paper.kind == "arxiv" and paper.identifier == "1810.04805"
    assert paper.metadata["doi"] == "10.18653/v1/N19-1423"


def test_landing_page_instead_of_pdf_is_rejected(settings: Settings) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>login</html>")

    with pytest.raises(FetchError, match="did not return a PDF"):
        fetcher(settings, handler).fetch(resolve("https://example.org/paper.pdf"))


def test_oversized_download_is_stopped(settings: Settings) -> None:
    small = settings.model_copy(update={"ingest": settings.ingest.model_copy(update={"max_mb": 0})})

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=PDF)

    with pytest.raises(FetchError, match="larger than"):
        fetcher(small, handler).fetch(resolve("https://example.org/paper.pdf"))
