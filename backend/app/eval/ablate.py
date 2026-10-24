"""Extraction arms for the Gemini ablations A2 (granularity) and A3 (quotes), run by
`app.eval.collect --arm <arm>` on the collected PDFs and TEI.

Every arm asks only for the scored fields (task, datasets, baselines, metrics,
hyperparameters, compute) through one prompt (prompts/ablation_extract.jinja), so the arms
differ only in what each call sees and whether it must quote:

    groups    2 calls: the front group for task, the experiments group for the rest (the
              production split), with quotes; the control arm for A2 and A3
    noquote   the same calls without quotes (A3: no evidence, so no grounding)
    whole     1 call over the text of all four groups, all fields, with quotes (A2)
    per_field 6 calls over that whole text, one field each, with quotes (A2)

Code URLs come from the regex rule as in production; quoted arms are grounded like
production (verify/grounding.py), so their evidence status and hallucination rate compare.
The production pipeline itself is the `pipeline` arm (A5 = that arm with --model).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, create_model

from app import prompts
from app.llm.client import LLMClient
from app.pipeline.extract.extractor import (
    _absorb,
    _add_code_urls,
    _dedupe,
    _metadata,
    _number_items,
)
from app.pipeline.extract.groups import GROUP_ROLES, GroupText, build_groups, render_block
from app.pipeline.extract.hints import find_hints
from app.schemas.document import ParsedDocument
from app.schemas.extraction import DatasetOut, HyperparameterOut, ItemOut, PaperExtraction

ARMS = ("groups", "noquote", "whole", "per_field")
FRONT_FIELDS = ["task"]
EXPERIMENT_FIELDS = ["datasets", "baselines", "metrics", "hyperparameters", "compute"]
SCORED = FRONT_FIELDS + EXPERIMENT_FIELDS
TEMPLATE = "ablation_extract"


class BareItemOut(BaseModel):
    value: str = Field(description="Short statement of the item, in your own words")
    confidence: float = Field(description="0 to 1: how sure you are")


class BareDatasetOut(BareItemOut):
    name: str = Field(description="Dataset name as written")
    split: str = Field(description="Split(s) used, or empty")
    size: str = Field(description="Size as stated, or empty")
    public: str = Field(description="'yes', 'no' or 'unknown'")


class BareHyperparameterOut(BareItemOut):
    name: str = Field(description="Hyperparameter name, e.g. learning rate")
    value_raw: str = Field(description="Value exactly as written, e.g. 3e-4")
    scope: str = Field(description="Where it applies (e.g. pre-training, fine-tuning), or empty")


QUOTED: dict[str, type[ItemOut]] = {"datasets": DatasetOut, "hyperparameters": HyperparameterOut}
BARE: dict[str, type[BareItemOut]] = {
    "datasets": BareDatasetOut,
    "hyperparameters": BareHyperparameterOut,
}


def output_schema(fields: list[str], quotes: bool) -> type[BaseModel]:
    """A response model holding only the requested fields."""
    spec: dict[str, Any] = {}
    for f in fields:
        cls = QUOTED.get(f, ItemOut) if quotes else BARE.get(f, BareItemOut)
        spec[f] = (list[cls], Field(default_factory=list))  # type: ignore[valid-type]
    name = "Ablation_" + "_".join(fields) + ("" if quotes else "_bare")
    model: type[BaseModel] = create_model(name, **spec)
    return model


def with_empty_quotes(out: BaseModel, fields: list[str]) -> BaseModel:
    """A no-quote answer in the quoted shape (empty quote: the item gets no evidence)."""
    data = {f: [QUOTED.get(f, ItemOut)(**x.model_dump(), quote="", chunk_id="")
                for x in getattr(out, f)] for f in fields}  # fmt: skip
    return output_schema(fields, True)(**data)


@dataclass
class Call:
    label: str
    fields: list[str]
    group: GroupText


def whole_text(doc: ParsedDocument, max_chars: int) -> GroupText:
    """Every block any group would see, once, in document order, up to max_chars."""
    groups = build_groups(doc, 10**9)
    ids = {b.id for g in groups.values() for b in g.blocks}
    blocks = [b for b in doc.blocks if b.id in ids]
    whole = GroupText("whole")
    used = 0
    for b in blocks:
        piece = render_block(b)
        if used + len(piece) > max_chars:
            whole.truncated = True
            break
        whole.blocks.append(b)
        used += len(piece) + 2
    whole.text = "\n\n".join(render_block(b) for b in whole.blocks)
    return whole


def plan(arm: str, doc: ParsedDocument, max_group_chars: int) -> list[Call]:
    if arm in ("groups", "noquote"):
        groups = build_groups(doc, max_group_chars)
        calls = [Call("front", FRONT_FIELDS, groups["front"]),
                 Call("experiments", EXPERIMENT_FIELDS, groups["experiments"])]  # fmt: skip
        return [c for c in calls if c.group.text]
    # The whole-paper arms see what the four production groups see together.
    whole = whole_text(doc, max_group_chars * len(GROUP_ROLES))
    if arm == "whole":
        return [Call("whole", SCORED, whole)]
    if arm == "per_field":
        return [Call(f, [f], whole) for f in SCORED]
    raise ValueError(f"unknown arm {arm!r}; one of {', '.join(ARMS)}")


def extract_arm(arm: str, doc: ParsedDocument, client: LLMClient,
                max_group_chars: int) -> tuple[PaperExtraction, int]:  # fmt: skip
    """Runs one arm; returns the extraction and the number of LLM calls made.
    A failed call raises (the collector then retries the paper on its next run)."""
    quotes = arm != "noquote"
    extraction = PaperExtraction(metadata=_metadata(doc, {}))
    pages = {b.id: b.page for b in doc.blocks}
    calls = 0
    for call in plan(arm, doc, max_group_chars):
        hints = find_hints(call.group.blocks) if set(call.fields) & set(EXPERIMENT_FIELDS) else []
        prompt = prompts.render(TEMPLATE, fields=call.fields, quotes=quotes, hints=hints,
                                text=call.group.text)  # fmt: skip
        result = client.generate_json(prompt, output_schema(call.fields, quotes),
                                      role="extraction")  # fmt: skip
        calls += 0 if result.meta.cached else 1
        out = result.value if quotes else with_empty_quotes(result.value, call.fields)
        _absorb(extraction, out, call.group, pages)
    _add_code_urls(extraction, doc)
    _dedupe(extraction)
    _number_items(extraction)
    return extraction, calls
