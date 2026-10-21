"""Toy schema used by the Phase 0 provider smoke tests."""

from pydantic import BaseModel, Field

TOY_TEXT = (
    "Attention Is All You Need. We evaluate the Transformer on the WMT 2014 English-German "
    "and WMT 2014 English-French translation tasks, and on English constituency parsing "
    "using the Penn Treebank."
)


class ToyExtraction(BaseModel):
    title: str = Field(description="Paper title")
    datasets: list[str] = Field(description="Dataset names exactly as written")
