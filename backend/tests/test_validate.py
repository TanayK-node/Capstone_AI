from pathlib import Path

import pytest

from app.config import IngestSection
from app.pipeline.ingest.validate import InvalidPdfError, validate_pdf

FIXTURES = Path(__file__).parent / "fixtures"


def test_valid_pdf() -> None:
    data = (FIXTURES / "paper_single.pdf").read_bytes()
    info = validate_pdf(data, IngestSection())
    assert info.page_count == 2
    assert info.has_text_layer
    assert len(info.sha256) == 64


@pytest.mark.parametrize(
    ("data", "cfg", "match"),
    [
        (b"<html>not a pdf</html>", IngestSection(), "not a PDF"),
        ((FIXTURES / "scanned.pdf").read_bytes(), IngestSection(), "no text layer"),
        ((FIXTURES / "paper_single.pdf").read_bytes(), IngestSection(max_pages=1), "2 pages"),
        ((FIXTURES / "paper_single.pdf").read_bytes(), IngestSection(max_mb=0), "larger than"),
    ],
)
def test_rejections(data: bytes, cfg: IngestSection, match: str) -> None:
    with pytest.raises(InvalidPdfError, match=match):
        validate_pdf(data, cfg)


def test_scanned_allowed_when_configured() -> None:
    data = (FIXTURES / "scanned.pdf").read_bytes()
    assert not validate_pdf(data, IngestSection(allow_scanned=True)).has_text_layer
