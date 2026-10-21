"""Extraction schema (SCOPE.md §6): what the pipeline returns about a paper.

Two layers:
  * LLM-facing models (`*Out`): flat, string-typed, small. Gemini and Qwen fill these via
    JSON-schema-constrained output. No Optional/union types: missing values are "".
  * API-facing models (`Item`, `PaperExtraction`, ...): what we store and serve. Evidence is
    resolved by Python (grounding.py), never trusted from the LLM.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.document import Box

GroundingStatus = Literal["verified", "partial", "unlocated", "unsupported", "unchecked"]

# ------------------------------------------------------------------ LLM output


class ItemOut(BaseModel):
    value: str = Field(description="Short statement of the item, in your own words")
    quote: str = Field(description="One sentence copied verbatim from the text that states it")
    chunk_id: str = Field(description="The [id] of the paragraph the quote comes from")
    confidence: float = Field(description="0 to 1: how sure you are")  # clamped in Python


class DatasetOut(ItemOut):
    name: str = Field(description="Dataset name as written")
    split: str = Field(description="Split(s) used, or empty")
    size: str = Field(description="Size as stated, or empty")
    public: str = Field(description="'yes', 'no' or 'unknown'")


class HyperparameterOut(ItemOut):
    name: str = Field(description="Hyperparameter name, e.g. learning rate")
    value_raw: str = Field(description="Value exactly as written, e.g. 3e-4")
    scope: str = Field(description="Where it applies (e.g. pre-training, fine-tuning), or empty")


class ClaimOut(ItemOut):
    kind: str = Field(description="'quantitative' (has a number) or 'qualitative'")


class FrontOut(BaseModel):
    """Abstract + introduction."""

    problem: list[ItemOut] = Field(default_factory=list)
    contributions: list[ItemOut] = Field(default_factory=list)
    task: list[ItemOut] = Field(default_factory=list)
    claims: list[ClaimOut] = Field(default_factory=list)


class MethodOut(BaseModel):
    method_summary: list[ItemOut] = Field(default_factory=list)
    novelty: list[ItemOut] = Field(default_factory=list)


class ExperimentsOut(BaseModel):
    datasets: list[DatasetOut] = Field(default_factory=list)
    baselines: list[ItemOut] = Field(default_factory=list)
    metrics: list[ItemOut] = Field(default_factory=list)
    hyperparameters: list[HyperparameterOut] = Field(default_factory=list)
    compute: list[ItemOut] = Field(default_factory=list)
    seeds_and_runs: list[ItemOut] = Field(default_factory=list)
    ablations: list[ItemOut] = Field(default_factory=list)


class ClosingOut(BaseModel):
    limitations: list[ItemOut] = Field(default_factory=list)
    future_work: list[ItemOut] = Field(default_factory=list)
    ethics: list[ItemOut] = Field(default_factory=list)


class SupportVerdictOut(BaseModel):
    id: int
    verdict: Literal["yes", "partial", "no"]


class SupportOut(BaseModel):
    verdicts: list[SupportVerdictOut] = Field(default_factory=list)


# ------------------------------------------------------------------ stored / API


class Evidence(BaseModel):
    chunk_id: str
    page: int
    bbox: Box | None = None
    boxes: list[Box] = Field(default_factory=list)  # sentence-level boxes to highlight
    quote: str
    grounding_status: GroundingStatus = "unchecked"
    match_score: float | None = None  # fuzzy match of the quote against the parsed text


class Item(BaseModel):
    id: str  # stable within one extraction: "contributions.2"
    value: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: float = 0.0
    source: Literal["llm", "rule"] = "llm"

    @property
    def verified(self) -> bool:
        return any(e.grounding_status == "verified" for e in self.evidence)


class Dataset(Item):
    name: str = ""
    split: str = ""
    size: str = ""
    public: str = "unknown"


class Hyperparameter(Item):
    name: str = ""
    value_raw: str = ""
    value_norm: float | None = None  # parsed in Python, never by the LLM
    scope: str = ""


class ResultEntry(BaseModel):
    """Filled from parsed tables in Phase 4 (M9)."""

    method: str
    dataset: str
    metric: str
    value: float
    std: float | None = None
    is_proposed: bool = False
    table_id: str
    cell: tuple[int, int]


class Claim(Item):
    kind: str = "qualitative"
    # Phase 4 (M8) fills these by recomputing deltas from tables in Python.
    metric: str | None = None
    dataset: str | None = None
    baseline: str | None = None
    delta: float | None = None
    verdict: str | None = None
    checked_cells: list[str] = Field(default_factory=list)


class Metadata(BaseModel):
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    venue: str | None = None
    year: str | None = None
    arxiv_id: str | None = None
    doi: str | None = None
    urls: list[str] = Field(default_factory=list)


ITEM_FIELDS = (
    "problem",
    "contributions",
    "task",
    "method_summary",
    "novelty",
    "baselines",
    "metrics",
    "compute",
    "seeds_and_runs",
    "ablations",
    "limitations",
    "future_work",
    "ethics",
    "code_urls",
)


class PaperExtraction(BaseModel):
    metadata: Metadata = Field(default_factory=Metadata)
    problem: list[Item] = Field(default_factory=list)
    contributions: list[Item] = Field(default_factory=list)
    task: list[Item] = Field(default_factory=list)
    method_summary: list[Item] = Field(default_factory=list)
    novelty: list[Item] = Field(default_factory=list)
    datasets: list[Dataset] = Field(default_factory=list)
    baselines: list[Item] = Field(default_factory=list)
    metrics: list[Item] = Field(default_factory=list)
    hyperparameters: list[Hyperparameter] = Field(default_factory=list)
    compute: list[Item] = Field(default_factory=list)
    seeds_and_runs: list[Item] = Field(default_factory=list)
    results: list[ResultEntry] = Field(default_factory=list)
    ablations: list[Item] = Field(default_factory=list)
    limitations: list[Item] = Field(default_factory=list)
    future_work: list[Item] = Field(default_factory=list)
    ethics: list[Item] = Field(default_factory=list)
    code_urls: list[Item] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)

    def all_items(self) -> list[tuple[str, Item]]:
        out: list[tuple[str, Item]] = []
        for name in (*ITEM_FIELDS, "datasets", "hyperparameters", "claims"):
            out += [(name, item) for item in getattr(self, name)]
        return out
