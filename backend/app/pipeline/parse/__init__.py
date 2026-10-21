"""PDF parsing (M2). Use get_parser(); it picks GROBID and falls back to PyMuPDF."""

from __future__ import annotations

import logging
from pathlib import Path

from app.config import Settings
from app.pipeline.parse.base import ParseError, Parser
from app.pipeline.parse.grobid import GrobidParser, parse_with_tei
from app.pipeline.parse.pymupdf_parser import PyMuPDFParser
from app.schemas.document import ParsedDocument

log = logging.getLogger("paperlens.parse")


class AutoParser:
    """GROBID when it is up, PyMuPDF otherwise. Caches GROBID's TEI next to the PDF."""

    name = "auto"

    def __init__(self, grobid: GrobidParser, fallback: PyMuPDFParser) -> None:
        self.grobid = grobid
        self.fallback = fallback

    def parse(self, pdf_path: Path) -> ParsedDocument:
        if self.grobid.is_alive():
            version = self.grobid.version()
            cached = pdf_path.with_name(f"grobid-{version}.tei.xml")
            try:
                if cached.exists():
                    tei = cached.read_bytes()
                else:
                    tei = self.grobid.fulltext_tei(pdf_path.read_bytes())
                    cached.write_bytes(tei)
                return parse_with_tei(pdf_path, tei, parser_version=version)
            except ParseError as exc:
                log.warning("grobid failed, falling back to pymupdf: %s", exc)
                doc = self.fallback.parse(pdf_path)
                doc.warnings.insert(0, f"GROBID failed ({exc}); used PyMuPDF")
                return doc
        doc = self.fallback.parse(pdf_path)
        doc.warnings.insert(0, "GROBID unreachable; used PyMuPDF")
        return doc


def get_parser(settings: Settings, name: str | None = None) -> Parser:
    choice = name or settings.parsing.parser
    grobid = GrobidParser(settings.grobid_url, timeout_s=settings.parsing.grobid_timeout_s)
    if choice == "grobid":
        return grobid
    if choice == "pymupdf":
        return PyMuPDFParser()
    return AutoParser(grobid, PyMuPDFParser())


__all__ = ["AutoParser", "ParseError", "Parser", "get_parser"]
