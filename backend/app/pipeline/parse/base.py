"""Parser interface: every parser turns a PDF into a ParsedDocument (SCOPE.md M2)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.schemas.document import ParsedDocument


class ParseError(Exception):
    """The parser could not produce a document (service down, unreadable PDF...)."""


class Parser(Protocol):
    name: str

    def parse(self, pdf_path: Path) -> ParsedDocument: ...
