"""PDF validation (M1): type, size, page count, text layer."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import pymupdf

from app.config import IngestSection


class InvalidPdfError(ValueError):
    """The file can't be processed; the message is shown to the user."""


@dataclass(frozen=True)
class PdfInfo:
    sha256: str
    page_count: int
    has_text_layer: bool
    size_bytes: int


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_pdf(data: bytes, cfg: IngestSection) -> PdfInfo:
    if len(data) > cfg.max_mb * 1024 * 1024:
        raise InvalidPdfError(f"PDF is larger than {cfg.max_mb} MB")
    if not data.lstrip()[:5].startswith(b"%PDF-"):
        raise InvalidPdfError("not a PDF file")
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise InvalidPdfError(f"PDF could not be opened: {exc}") from exc
    with doc:
        if doc.needs_pass:
            raise InvalidPdfError("PDF is password-protected")
        pages = doc.page_count
        if pages == 0:
            raise InvalidPdfError("PDF has no pages")
        if pages > cfg.max_pages:
            raise InvalidPdfError(f"PDF has {pages} pages; the limit is {cfg.max_pages}")
        # Text layer: enough extractable characters on the first few pages.
        chars = sum(len(doc[i].get_text().strip()) for i in range(min(pages, 3)))
        has_text = chars >= 200
    if not has_text and not cfg.allow_scanned:
        raise InvalidPdfError("PDF has no text layer (it looks scanned); OCR is not supported")
    return PdfInfo(sha256(data), pages, has_text, len(data))
