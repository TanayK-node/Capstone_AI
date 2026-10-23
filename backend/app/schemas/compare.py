"""Multi-paper comparison (F14): what several analysed papers share, side by side."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ComparedPaper(BaseModel):
    id: str
    title: str
    year: str | None = None
    method: list[str] = Field(default_factory=list)  # names the paper's own method goes by


class Cell(BaseModel):
    values: list[str] = Field(default_factory=list)  # empty = not reported by this paper
    pages: list[int] = Field(default_factory=list)


class MatrixRow(BaseModel):
    group: str  # "Datasets", "Metrics", "Training", ...
    label: str
    cells: list[Cell]  # one per paper, in ComparedPaper order
    shared: bool = False  # reported by two or more papers


class ResultCell(BaseModel):
    method: str = ""
    text: str = ""  # as printed
    value: float | None = None
    is_best: bool = False  # best in its own table column
    table: str | None = None
    page: int | None = None


class SharedResult(BaseModel):
    """One table column (same header text) reported by several papers."""

    label: str
    higher_is_better: bool | None = None
    cells: list[ResultCell]  # one per paper


class Comparison(BaseModel):
    papers: list[ComparedPaper]
    rows: list[MatrixRow] = Field(default_factory=list)
    results: list[SharedResult] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
