"""Reviewer mode (F15): an OpenReview-style review grounded in the paper and the analyses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import Evidence

# ------------------------------------------------------------------ LLM output


class PointOut(BaseModel):
    point: str = Field(description="One or two sentences")
    quote: str = Field(
        description="ONE sentence copied verbatim from the paper text that the point rests "
        "on, or '' if it rests only on the analysis facts"
    )
    chunk_id: str = Field(description="The [id] of the paragraph the quote comes from, or ''")


class ReviewOut(BaseModel):
    summary: str = Field(description="3-5 sentences: what the paper does and finds")
    strengths: list[PointOut] = Field(default_factory=list)
    weaknesses: list[PointOut] = Field(default_factory=list)
    missing_ablations: list[PointOut] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------ stored / API


class ReviewPoint(BaseModel):
    point: str
    evidence: list[Evidence] = Field(default_factory=list)


class Finding(BaseModel):
    """A fact the analyses established in Python (not written by the LLM)."""

    source: Literal["reproducibility", "claims", "code"]
    text: str
    evidence: list[Evidence] = Field(default_factory=list)


class Review(BaseModel):
    summary: str
    strengths: list[ReviewPoint] = Field(default_factory=list)
    weaknesses: list[ReviewPoint] = Field(default_factory=list)
    missing_ablations: list[ReviewPoint] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
