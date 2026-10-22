"""Citation graph and novelty positioning (M12, SCOPE.md F13)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import Evidence

Relation = Literal["extends", "uses", "compares_to", "differs_from"]

# ------------------------------------------------------------------ LLM output


class PositionOut(BaseModel):
    ref: str = Field(description="The [R..] marker of the reference, e.g. R3")
    relation: Relation = Field(
        description="extends = builds on it; uses = uses it as a component, dataset or tool; "
        "compares_to = reports results against it; differs_from = says it does something else"
    )
    statement: str = Field(description="One sentence: how this paper relates to the reference")
    quote: str = Field(
        description="A sentence copied verbatim from THIS paper's text that supports the "
        "statement; empty if the paper's text given does not say"
    )
    chunk_id: str = Field(description="The [id] of the paragraph the quote comes from")


class NoveltyOut(BaseModel):
    summary: str = Field(
        description="2-4 sentences: what is new in this paper relative to these references"
    )
    positions: list[PositionOut] = Field(default_factory=list)


# ------------------------------------------------------------------ stored / API


class GraphNode(BaseModel):
    id: str  # "paper", "ref:b12" (in the PDF's list) or "s2:<paperId>"
    kind: Literal["paper", "reference", "citation"]
    title: str
    year: int | None = None
    venue: str | None = None
    authors: list[str] = Field(default_factory=list)  # first three
    citation_count: int | None = None  # from Semantic Scholar
    influential: bool = False  # S2 "isInfluential" (a reference / citation that matters)
    mentions: int = 0  # times this paper cites it in its text (references only)
    ref_id: str | None = None  # the reference in the PDF ("b12"), for highlighting
    url: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)  # sentences citing it


class NoveltyPosition(BaseModel):
    node: str  # GraphNode.id
    title: str
    relation: Relation
    statement: str
    evidence: list[Evidence] = Field(default_factory=list)


class Novelty(BaseModel):
    summary: str
    positions: list[NoveltyPosition] = Field(default_factory=list)


class ContextReport(BaseModel):
    source: Literal["semantic_scholar", "pdf"]
    paper: GraphNode
    references: list[GraphNode] = Field(default_factory=list)  # top, most important first
    citations: list[GraphNode] = Field(default_factory=list)
    reference_count: int = 0  # all references (S2, else the PDF's list)
    citation_count: int | None = None
    influential_citation_count: int | None = None
    # S2 cannot sort citing papers: they are picked from the most recent ones it returns, and
    # for a much-cited paper that is only a sample (citations_scanned < citation_count).
    citations_scanned: int = 0
    novelty: Novelty | None = None
    warnings: list[str] = Field(default_factory=list)
