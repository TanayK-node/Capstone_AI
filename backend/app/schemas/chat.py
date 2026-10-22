"""Grounded chat (M11): answers cite the paper's passages; no citation, no answer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[ChatTurn] = Field(default_factory=list)


class ChatOut(BaseModel):
    """LLM output."""

    answerable: bool = Field(description="false if the passages do not answer the question")
    answer: str = Field(description="The answer, citing passages like [P2] after each statement")


class Citation(BaseModel):
    marker: str  # "P2", as written in the answer
    chunk_id: str
    page: int
    section: str
    text: str  # the passage (shown on hover)
    boxes: list[dict[str, float]] = Field(default_factory=list)


class Retrieved(BaseModel):
    chunk_id: str
    page: int
    section: str
    score: float
    bm25: float
    cosine: float | None


class ChatAnswer(BaseModel):
    answer: str
    answered: bool  # False: refused (nothing relevant, or the answer could not be grounded)
    citations: list[Citation] = Field(default_factory=list)
    retrieved: list[Retrieved] = Field(default_factory=list)
    retrieval: str  # "hybrid" (BM25 + embeddings) or "bm25"
    provider: str | None = None
    model: str | None = None
    prompt_version: str | None = None
