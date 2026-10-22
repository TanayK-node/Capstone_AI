"""Results tables (M9, SCOPE.md F9): parsed table grids turned into typed results.

Built deterministically from the parse (no LLM): column headers from the header rows, row
labels from the leading text cells, numbers from tables.parse_number, best values per column.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResultColumn(BaseModel):
    index: int
    header: str  # header text directly above this column (reliable)
    group: str = ""  # a spanning header guessed to cover it ("BLEU" over EN-DE / EN-FR)
    numeric: bool = False
    higher_is_better: bool | None = None  # None = unknown direction (no best marked)


class ResultCell(BaseModel):
    col: int
    text: str
    value: float | None = None
    std: float | None = None
    is_percent: bool = False
    is_bold: bool = False  # bold in the PDF: authors usually bold the best value
    is_best: bool = False  # computed in Python from the column direction


class ResultRow(BaseModel):
    index: int  # row in the table grid
    label: str  # method / system name
    group: str = ""  # section row above it ("Methods using ResNet-50:")
    is_proposed: bool = False
    cells: list[ResultCell] = Field(default_factory=list)


class ResultsTable(BaseModel):
    table_id: str  # block id
    label: str | None
    caption: str
    page: int
    columns: list[ResultColumn]
    rows: list[ResultRow]
    proposed_names: list[str] = Field(default_factory=list)  # what "is_proposed" matched
