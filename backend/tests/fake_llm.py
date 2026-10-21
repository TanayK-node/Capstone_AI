"""A fake provider that answers extraction and verification prompts like a model would.

Extraction: for each list field the schema asks for, it returns one item quoting a real
sentence from the tagged paragraphs in the prompt ("[b0012] ..."), so grounding can locate
it. Field-specific keywords pick sensible sentences. Verification: every item is "yes".
An optional invented quote lets tests check that hallucinated evidence is caught.
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


class FakePaperProvider:
    name = "gemini"

    def __init__(self, invented_quote_for: str | None = None) -> None:
        self.calls: list[ProviderRequest] = []
        self.invented_quote_for = invented_quote_for

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

    def list_models(self) -> list[str]:
        return ["fake"]
