"""Files on disk: data_dir/papers/<sha256>/paper.pdf (+ LaTeX source, GROBID TEI cache)."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings


def paper_dir(settings: Settings, paper_id: str) -> Path:
    if not paper_id.isalnum():  # sha256 hex; guards against path traversal via the API
        raise ValueError("invalid paper id")
    return Path(settings.app.data_dir) / "papers" / paper_id


def pdf_path(settings: Settings, paper_id: str) -> Path:
    return paper_dir(settings, paper_id) / "paper.pdf"


def save_pdf(settings: Settings, paper_id: str, data: bytes) -> Path:
    path = pdf_path(settings, paper_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)  # atomic: a crashed upload never leaves a half-written PDF
    return path


def save_latex_source(settings: Settings, paper_id: str, data: bytes) -> Path:
    path = paper_dir(settings, paper_id) / "source.tar.gz"
    path.write_bytes(data)
    return path
