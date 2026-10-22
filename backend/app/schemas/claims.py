"""Claim verification (M8, SCOPE.md F8).

The LLM only reads each claim into fields, copying numbers as written (`*Out`). Python finds
the table cells, recomputes values and deltas, and assigns the verdict (CLAUDE.md rule 4).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import Evidence

ClaimKind = Literal["score", "improvement", "factor", "qualitative"]
Verdict = Literal["supported", "contradicted", "unsupported", "weakly_supported", "unverifiable"]

# ------------------------------------------------------------------ LLM output


class ClaimParseOut(BaseModel):
    id: int = Field(description="The claim number from the list")
    kind: ClaimKind = Field(
        description="score: a method reaches a value; improvement: beats a baseline by an "
        "amount; factor: N times fewer/faster/smaller; qualitative: no number to check"
    )
    method: str = Field(description="The method the claim is about, as written ('' if ours)")
    baseline: str = Field(description="What it is compared with, as written, or ''")
    dataset: str = Field(description="Dataset / benchmark / task, as written, or ''")
    metric: str = Field(description="Metric, as written (BLEU, top-1 accuracy, F1...), or ''")
    value: str = Field(description="kind=score: the value exactly as written, else ''")
    delta: str = Field(description="kind=improvement/factor: the amount as written, else ''")
    delta_unit: Literal["points", "percent", "times", ""] = Field(
        description="points: absolute; percent: written with %; times: a factor"
    )
    comparator: Literal["exact", "at_least", "at_most", "approx"] = Field(
        description="'over 2' / 'more than' -> at_least; 'up to' -> at_most; 'about' -> approx"
    )
    direction: Literal["higher", "lower", ""] = Field(
        description="Is the method's number higher or lower than the baseline's?"
    )


class ClaimsParseOut(BaseModel):
    claims: list[ClaimParseOut] = Field(default_factory=list)


# ------------------------------------------------------------------ stored / API


class CheckedCell(BaseModel):
    table_id: str
    table_label: str | None
    row: int
    col: int
    row_label: str
    column: str  # header (with its group when it has one)
    text: str  # as printed
    value: float
    role: Literal["method", "baseline"]


class ClaimCheck(BaseModel):
    id: str  # "claims.3": the extraction claim it checks
    text: str  # the claim sentence
    evidence: list[Evidence] = Field(default_factory=list)
    kind: ClaimKind = "qualitative"
    method: str = ""
    baseline: str = ""
    dataset: str = ""
    metric: str = ""
    comparator: str = "exact"
    direction: str = ""  # "higher" / "lower": which way the claim says the method moved
    claimed_value: float | None = None
    claimed_delta: float | None = None
    delta_unit: str = ""
    # Recomputed in Python from the table cells (never by the LLM).
    table_value: float | None = None
    baseline_value: float | None = None
    recomputed_delta: float | None = None  # absolute, method minus baseline
    recomputed_relative: float | None = None  # percent change vs the baseline
    recomputed_factor: float | None = None
    verdict: Verdict = "unverifiable"
    explanation: str = ""
    checked_cells: list[CheckedCell] = Field(default_factory=list)


class ClaimReport(BaseModel):
    tolerance: float
    claims: list[ClaimCheck] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
