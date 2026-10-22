"""Reproducibility scorecard (M6, SCOPE.md F5): checklist items with status and evidence.

LLM-facing models (`*Out`) are flat and small; everything else is filled by Python.
The score is computed in Python from item statuses and weights (CLAUDE.md rule 4).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import Evidence

# present / partial / missing as in SCOPE.md F5; not_applicable is left out of the score;
# unknown = could not be decided (e.g. a GitLab repo, or the LLM call failed), also left out.
ItemStatus = Literal["present", "partial", "missing", "not_applicable", "unknown"]
ItemSource = Literal["rule", "extraction", "repo", "llm", "none"]

POINTS: dict[str, float] = {"present": 1.0, "partial": 0.5, "missing": 0.0}

# ------------------------------------------------------------------ checklist config


class ChecklistGroup(BaseModel):
    id: str
    label: str
    weight: float


class ChecklistItem(BaseModel):
    id: str
    group: str
    weight: float = 1.0
    rule: str | None = None
    description: str
    question: str = ""
    guidance: str = ""  # what present / partial means for this item (shown to the LLM)


class Checklist(BaseModel):
    version: int
    groups: list[ChecklistGroup]
    items: list[ChecklistItem]


# ------------------------------------------------------------------ LLM output


class ReproItemOut(BaseModel):
    id: str = Field(description="The checklist item id, copied from the list")
    status: Literal["present", "partial", "missing", "not_applicable"]
    quote: str = Field(description="For present/partial: one sentence copied verbatim, else empty")
    chunk_id: str = Field(description="The [id] of the paragraph or table the quote comes from")
    note: str = Field(description="One short sentence explaining the status")


class ReproOut(BaseModel):
    items: list[ReproItemOut] = Field(default_factory=list)


# ------------------------------------------------------------------ stored / API


class RepoInfo(BaseModel):
    """What the GitHub API says about the paper's repository (no clone in Phase 3)."""

    url: str
    host: str  # github.com, gitlab.com, huggingface.co ...
    owner: str | None = None
    name: str | None = None
    reachable: bool | None = None  # None = not checked (non-GitHub host, network error)
    license: str | None = None
    stars: int | None = None
    pushed_at: str | None = None
    archived: bool | None = None
    root_files: list[str] = Field(default_factory=list)
    readme_excerpt: str = ""
    error: str | None = None


class ItemResult(BaseModel):
    id: str
    group: str
    description: str
    weight: float
    status: ItemStatus = "unknown"
    source: ItemSource = "none"
    note: str = ""
    evidence: list[Evidence] = Field(default_factory=list)
    question: str = ""  # filled for missing / partial items


class GroupScore(BaseModel):
    id: str
    label: str
    weight: float
    score: float | None  # 0-1; None when no item of the group could be scored
    counts: dict[str, int] = Field(default_factory=dict)


class Scorecard(BaseModel):
    checklist_version: int
    score: float | None  # 0-100
    groups: list[GroupScore]
    items: list[ItemResult]
    missing: list[str] = Field(default_factory=list)  # item ids, heaviest first
    questions: list[str] = Field(default_factory=list)
    repo: RepoInfo | None = None
    warnings: list[str] = Field(default_factory=list)
