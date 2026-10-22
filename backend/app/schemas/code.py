"""Paper-code consistency (M7, SCOPE.md F7). Everything here is computed without an LLM."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import Evidence
from app.schemas.repro import RepoInfo

CodeStatus = Literal[
    "ok",  # cloned, scanned, compared
    "no_repo",  # no repository found
    "needs_confirmation",  # best candidate is a guess: ask the user (POST /code/confirm)
    "clone_failed",
    "too_large",
    "scan_failed",
]
RowStatus = Literal["match", "mismatch", "only_in_paper", "only_in_code"]


class RepoCandidate(BaseModel):
    url: str
    source: Literal["paper", "github_search", "user"]
    confidence: float  # 0-1
    reason: str
    subdir: str | None = None  # ".../tree/main/examples/distillation" -> examples/distillation


class CodeParam(BaseModel):
    """One value found in the repository by the static scanner."""

    name: str  # as written ("--lr", "optimizer.lr", "learning_rate")
    canonical: str | None = None  # "learning_rate" (compare.py synonym table)
    value: str  # as written
    value_norm: float | None = None
    file: str
    line: int | None = None
    kind: str  # argparse / flags / click / dataclass / constant / attr / kwarg / config / readme


class Comparison(BaseModel):
    canonical: str
    status: RowStatus
    paper_name: str = ""
    paper_value: str = ""
    paper_scope: str = ""
    paper_evidence: list[Evidence] = Field(default_factory=list)
    code_values: list[CodeParam] = Field(default_factory=list)
    note: str = ""


class CodeReport(BaseModel):
    status: CodeStatus
    repo: RepoInfo | None = None
    candidates: list[RepoCandidate] = Field(default_factory=list)
    commit: str | None = None
    sandbox: str | None = None  # "docker" (no network, read-only) or "process"
    files_scanned: int = 0
    params_found: int = 0
    comparisons: list[Comparison] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    reproduce_issues: int | None = None  # open issues mentioning "reproduce" (GitHub API)
    warnings: list[str] = Field(default_factory=list)
