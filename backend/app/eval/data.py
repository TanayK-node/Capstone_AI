"""Gold items (eval/gold/extraction_gold.csv) and PaperLens predictions to score against them.

Predictions come from either
- a check_extract report.md (the Markdown export of every paper, "## <paper id>" first), or
- a directory of extraction JSON files named <paper id>.json (GET /export?format=json, or
  the per-paper files check_extract writes to phase2_check/extractions/).
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from dataclasses import field as dc_field
from pathlib import Path

from app.pipeline.export import SECTIONS
from app.schemas.extraction import Dataset, Hyperparameter, PaperExtraction

# Fields scored item by item. Prose fields (problem, contributions, ...) are only checked for
# grounding: there is no single right list of them to compare with.
SCORED_FIELDS = ("task", "datasets", "baselines", "metrics", "hyperparameters", "compute",
                 "code_urls")  # fmt: skip
_HEADINGS = {heading: name for name, heading in SECTIONS}


@dataclass
class GoldItem:
    paper_id: str
    field: str
    value: str
    name: str = ""  # hyperparameters: canonical name ("learning_rate")
    aliases: list[str] = dc_field(default_factory=list)
    page: str = ""
    note: str = ""

    @property
    def names(self) -> list[str]:
        """Every way of writing the value (hyperparameters: the value's spellings)."""
        return [self.value, *self.aliases]


@dataclass
class PredItem:
    paper_id: str
    field: str
    value: str
    name: str = ""  # hyperparameters: the name as extracted ("learning rate")
    scope: str = ""
    status: str = "no evidence"  # best grounding status of its evidence
    quote: str = ""
    page: int | None = None


def load_gold(path: Path) -> list[GoldItem]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        aliases = [a.strip() for a in (r.get("aliases") or "").split("|") if a.strip()]
        out.append(GoldItem(paper_id=r["paper_id"].strip(), field=r["field"].strip(),
                            value=r["value"].strip(), name=(r.get("name") or "").strip(),
                            aliases=aliases, page=(r.get("page") or "").strip(),
                            note=(r.get("note") or "").strip()))  # fmt: skip
    return out


def load_predictions(source: Path) -> list[PredItem]:
    if source.is_dir():
        out: list[PredItem] = []
        for f in sorted(source.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            out += from_extraction(f.stem, PaperExtraction.model_validate(data))
        return out
    return from_markdown(source.read_text(encoding="utf-8"))


def _best_status(statuses: list[str]) -> str:
    for s in ("verified", "partial", "unsupported", "unlocated", "unchecked"):
        if s in statuses:
            return s
    return "no evidence"


def from_extraction(paper_id: str, ex: PaperExtraction) -> list[PredItem]:
    out: list[PredItem] = []
    for name, _ in SECTIONS:
        for item in getattr(ex, name):
            ev = item.evidence[0] if item.evidence else None
            pred = PredItem(paper_id=paper_id, field=name, value=item.value,
                            status=_best_status([e.grounding_status for e in item.evidence]),
                            quote=ev.quote if ev else "", page=ev.page if ev else None)  # fmt: skip
            if isinstance(item, Hyperparameter):
                pred.name, pred.value, pred.scope = (
                    item.name,
                    item.value_raw or item.value,
                    item.scope,
                )
            elif isinstance(item, Dataset) and item.name:
                pred.value = item.name
            out.append(pred)
    return out


_ITEM = re.compile(r"^- (?P<label>.*?) _\[(?P<status>[a-z ]+)\]_\s*$")
_QUOTE = re.compile(r"^\s+> p\. (?P<page>\d+): “(?P<quote>.*)”\s*$")
_HP = re.compile(r"^(?P<name>.+?)(?: \((?P<scope>[^()]*)\))?: (?P<value>.+)$")


def from_markdown(text: str) -> list[PredItem]:
    """Items from a check_extract report.md: '## <id>' starts a paper, '## <Heading>' a field."""
    out: list[PredItem] = []
    paper = field_name = None
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            if heading in _HEADINGS:
                field_name = _HEADINGS[heading]
            else:  # a paper id
                paper, field_name = heading, None
            continue
        if paper is None or field_name is None:
            continue
        if m := _ITEM.match(line):
            pred = PredItem(paper_id=paper, field=field_name, value=m["label"].strip(),
                            status=m["status"])  # fmt: skip
            if field_name == "hyperparameters" and (h := _HP.match(pred.value)):
                pred.name, pred.scope, pred.value = h["name"], h["scope"] or "", h["value"]
            elif field_name == "datasets":
                pred.value = re.sub(r"\s*\([^()]*\)\s*$", "", pred.value)  # "(split, size)"
            out.append(pred)
        elif (q := _QUOTE.match(line)) and out and not out[-1].quote:
            out[-1].quote, out[-1].page = q["quote"], int(q["page"])
    return out
