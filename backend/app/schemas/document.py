"""ParsedDocument: the parser-independent output of M2 (SCOPE.md §5).

Coordinates are PDF points with the origin at the top-left of the page, the convention shared
by GROBID, PyMuPDF and the PDF.js viewport, so the UI can draw boxes without flipping axes.
Pages are 1-indexed.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

BlockType = Literal[
    "title",
    "heading",
    "paragraph",
    "table",
    "figure",
    "caption",
    "equation",
    "footnote",
    "reference",
]

SectionRole = Literal[
    "abstract",
    "introduction",
    "related_work",
    "background",
    "method",
    "experiments",
    "results",
    "ablation",
    "discussion",
    "limitations",
    "conclusion",
    "acknowledgements",
    "references",
    "appendix",
    "other",
]


class Box(BaseModel):
    page: int
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def area(self) -> float:
        return max(0.0, self.x1 - self.x0) * max(0.0, self.y1 - self.y0)


class Sentence(BaseModel):
    text: str
    boxes: list[Box] = Field(default_factory=list)


class TableCell(BaseModel):
    text: str
    row: int
    col: int
    # Filled by tables.normalize_table; the LLM never parses numbers (CLAUDE.md rule 4).
    value: float | None = None
    std: float | None = None
    is_percent: bool = False
    is_bold: bool = False
    is_header: bool = False


class TableData(BaseModel):
    label: str | None = None  # "Table 2"
    caption: str = ""
    n_rows: int = 0
    n_cols: int = 0
    header_rows: int = 0
    cells: list[TableCell] = Field(default_factory=list)

    def grid(self) -> list[list[str]]:
        rows = [["" for _ in range(self.n_cols)] for _ in range(self.n_rows)]
        for cell in self.cells:
            if cell.row < self.n_rows and cell.col < self.n_cols:
                rows[cell.row][cell.col] = cell.text
        return rows


class Block(BaseModel):
    id: str  # stable within one parse: "b0001"
    type: BlockType
    order: int  # reading order
    page: int  # first page the block appears on
    bbox: Box | None  # union of the block's boxes on its first page
    boxes: list[Box] = Field(default_factory=list)  # every box, for multi-column/page highlight
    section_path: list[str] = Field(default_factory=list)
    text: str
    sentences: list[Sentence] = Field(default_factory=list)
    table: TableData | None = None
    label: str | None = None  # "Table 2", "Figure 3", "(4)"
    role: str | None = None  # section role, set by the structure stage (M3)


class PageInfo(BaseModel):
    number: int
    width: float
    height: float


class Author(BaseModel):
    name: str
    affiliation: str | None = None


class Reference(BaseModel):
    id: str
    text: str
    title: str | None = None
    year: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    boxes: list[Box] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    title: str | None = None
    authors: list[Author] = Field(default_factory=list)
    abstract: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    year: str | None = None
    venue: str | None = None


class ParsedDocument(BaseModel):
    parser: str  # "grobid", "pymupdf", ...
    parser_version: str
    pages: list[PageInfo]
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    blocks: list[Block]
    references: list[Reference] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def tables(self) -> list[Block]:
        return [b for b in self.blocks if b.type == "table"]


def union_box(boxes: list[Box]) -> Box | None:
    """Bounding box of the boxes on the first page they appear on."""
    if not boxes:
        return None
    page = boxes[0].page
    same = [b for b in boxes if b.page == page]
    return Box(
        page=page,
        x0=min(b.x0 for b in same),
        y0=min(b.y0 for b in same),
        x1=max(b.x1 for b in same),
        y1=max(b.y1 for b in same),
    )
