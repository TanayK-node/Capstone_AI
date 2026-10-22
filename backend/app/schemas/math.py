"""Equations and notation glossary (M10, SCOPE.md F11)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import Evidence

# ------------------------------------------------------------------ LLM output


class SymbolOut(BaseModel):
    symbol: str = Field(
        description="The symbol as written in the paper's LaTeX, e.g. d_k or \\alpha"
    )
    meaning: str = Field(description="What it denotes, in a few words")
    quote: str = Field(description="One sentence copied verbatim from the text that defines it")
    chunk_id: str = Field(description="The [id] of the paragraph the quote comes from")


class GlossaryOut(BaseModel):
    symbols: list[SymbolOut] = Field(default_factory=list)


# ------------------------------------------------------------------ stored / API


class Equation(BaseModel):
    id: str  # "eq1", in document order
    number: str | None = None  # "(3)" as printed, when numbered
    latex: str | None = None  # from the arXiv source, ready for KaTeX
    text: str = ""  # from the PDF (GROBID), when there is no source
    block_id: str | None = None  # the PDF equation block, for highlighting
    page: int | None = None
    boxes: list[dict[str, float]] = Field(default_factory=list)
    source: Literal["latex", "pdf"] = "pdf"


class Symbol(BaseModel):
    symbol: str
    meaning: str
    evidence: list[Evidence] = Field(default_factory=list)
    equations: list[str] = Field(default_factory=list)  # ids of equations that use it


class MathReport(BaseModel):
    latex_available: bool
    equations: list[Equation] = Field(default_factory=list)
    symbols: list[Symbol] = Field(default_factory=list)
    macros: dict[str, str] = Field(default_factory=dict)  # the paper's \newcommands, for KaTeX
    warnings: list[str] = Field(default_factory=list)
