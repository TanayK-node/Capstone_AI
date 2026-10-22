"""A fake provider that answers extraction and verification prompts like a model would.

Extraction: for each list field the schema asks for, it returns one item quoting a real
sentence from the tagged paragraphs in the prompt ("[b0012] ..."), so grounding can locate
it. Field-specific keywords pick sensible sentences. Verification: every item is "yes".
An optional invented quote lets tests check that hallucinated evidence is caught.
Reproducibility checklist: items with a keyword below are "present" with a quoted sentence,
items the prompt lists rule "pattern match" sentences for are "partial" quoting the first
match (a careful model: one mention is not full coverage); the rest "missing".
`repro_invented` makes one item cite a sentence that is not in the paper.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.llm.types import ProviderRequest, ProviderResponse

_TAGGED = re.compile(r"^\[(b\d+)\] (.+)$", re.MULTILINE)
_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
KEYWORDS = {
    "contributions": "contributions",
    "hyperparameters": "learning rate",
    "compute": "A100",
    "seeds_and_runs": "seeds",
    "limitations": "only evaluate",
    "datasets": "FLORES",
    "claims": "BLEU",
}


REPRO_KEYWORDS = {
    "datasets_named": "Test BLEU",
    "eval_protocol": "Test BLEU",
    "hyperparameters_all": "learning rate",
}


class FakePaperProvider:
    name = "gemini"

    def __init__(
        self,
        invented_quote_for: str | None = None,
        repro_invented: str | None = None,
        repro_ignores_matches: bool = False,  # a model that answers "missing" regardless
    ) -> None:
        self.calls: list[ProviderRequest] = []
        self.invented_quote_for = invented_quote_for
        self.repro_invented = repro_invented
        self.repro_ignores_matches = repro_ignores_matches

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self.calls.append(request)
        schema = request.json_schema or {}
        fields = list(schema.get("properties", {}))
        if fields == ["verdicts"]:
            ids = [int(i) for i in re.findall(r"^(\d+)\. FIELD:", request.prompt, re.M)]
            return ProviderResponse(
                json.dumps({"verdicts": [{"id": i, "verdict": "yes"} for i in ids]})
            )
        paragraphs = _TAGGED.findall(request.prompt)
        if fields == ["answerable", "answer"]:
            return ProviderResponse(json.dumps(self._chat(request.prompt)))
        if fields == ["claims"] and "Below are claims" in request.prompt:
            return ProviderResponse(json.dumps({"claims": self._claims(request.prompt)}))
        if fields == ["items"]:
            return ProviderResponse(json.dumps({"items": self._checklist(request, paragraphs)}))
        out: dict[str, Any] = {}
        for name in fields:
            out[name] = [self._item(name, paragraphs)] if paragraphs else []
        return ProviderResponse(json.dumps(out), input_tokens=100, output_tokens=50)

    def _item(self, name: str, paragraphs: list[tuple[str, str]]) -> dict[str, Any]:
        block_id, sentence = paragraphs[0][0], _SENT.split(paragraphs[0][1])[0]
        key = KEYWORDS.get(name)
        for bid, text in paragraphs:
            hit = next((s for s in _SENT.split(text) if key and key in s), None)
            if hit:
                block_id, sentence = bid, hit
                break
        if name == self.invented_quote_for:
            sentence = "This sentence does not appear anywhere in the paper at all."
        item: dict[str, Any] = {
            "value": f"{name}: {sentence[:60]}",
            "quote": sentence,
            "chunk_id": block_id,
            "confidence": 0.8,
        }
        if name == "datasets":
            item |= {"name": "FLORES-200", "split": "test", "size": "", "public": "yes"}
        if name == "hyperparameters":
            item |= {"name": "learning rate", "value_raw": "3e-4", "scope": ""}
        if name == "claims":
            item |= {"kind": "quantitative"}
        return item

    def _checklist(
        self, request: ProviderRequest, paragraphs: list[tuple[str, str]]
    ) -> list[dict[str, str]]:
        section = request.prompt.split("Checklist items:")[1].split("Paper text:")[0]
        ids = re.findall(r"^- (\w+): ", section, re.M)
        matches: dict[str, tuple[str, str]] = {}
        current = ""
        for line in section.splitlines():
            if m := re.match(r"^- (\w+): ", line):
                current = m.group(1)
            elif (m := re.match(r"^\s+pattern match[^:]*: \[(\w+)\] (.+)$", line)) and current:
                matches.setdefault(current, (m.group(1), m.group(2)))
        answers = []
        for item_id in ids:
            if (
                item_id in matches
                and item_id != self.repro_invented
                and not self.repro_ignores_matches
            ):
                bid, quote = matches[item_id]
                answers.append(
                    {"id": item_id, "status": "partial", "quote": quote, "chunk_id": bid,
                     "note": "mentioned for one setting"}
                )  # fmt: skip
                continue
            key = REPRO_KEYWORDS.get(item_id)
            hit = next(
                ((bid, s) for bid, t in paragraphs for s in _SENT.split(t) if key and key in s),
                None,
            )
            if item_id == self.repro_invented:
                hit = (paragraphs[0][0], "We release every checkpoint and all training logs.")
            if hit is None:
                answers.append(
                    {"id": item_id, "status": "missing", "quote": "", "chunk_id": "", "note": "-"}
                )
                continue
            answers.append(
                {"id": item_id, "status": "present", "quote": hit[1], "chunk_id": hit[0],
                 "note": "stated"}
            )  # fmt: skip
        return answers

    def _chat(self, prompt: str) -> dict[str, object]:
        """Answer from the first passage, citing it, as a grounded model would."""
        first = re.search(r"^\[(P\d+)\] \([^)]*\) (.+?)$", prompt, re.M)
        if first is None:
            return {"answerable": False, "answer": "The passages do not say."}
        sentence = _SENT.split(first.group(2))[0]
        return {"answerable": True, "answer": f"{sentence} [{first.group(1)}] [P99]"}

    def _claims(self, prompt: str) -> list[dict[str, str | int]]:
        """Read "N. claim" lines with a few patterns, as a model would fill the fields."""
        out: list[dict[str, str | int]] = []
        for num, text in re.findall(r"^(\d+)\. (.+)$", prompt, re.M):
            claim: dict[str, str | int] = {
                "id": int(num), "kind": "qualitative", "method": "", "baseline": "",
                "dataset": "", "metric": "", "value": "", "delta": "", "delta_unit": "",
                "comparator": "exact", "direction": "",
            }  # fmt: skip
            if m := re.search(r"on the ([\w-]+) benchmark", text):
                claim["dataset"] = m.group(1)
            if m := re.search(r"improves (\w+) by ([\d.]+) points over an? (?:dense )?(\w+)", text):
                claim |= {"kind": "improvement", "metric": m.group(1), "delta": m.group(2),
                          "delta_unit": "points", "baseline": m.group(3),
                          "direction": "higher"}  # fmt: skip
            elif m := re.search(r"(?:achieves|reaches) ([\d.]+) (\w+)", text):
                claim |= {"kind": "score", "value": m.group(1), "metric": m.group(2)}
            out.append(claim)
        return out

    def list_models(self) -> list[str]:
        return ["fake"]
