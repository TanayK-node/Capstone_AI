"""Agreement between the scorecard and human annotations (Phase 3 exit, SCOPE.md §8).

Gold file: CSV with columns paper_id, item_id, status (+ any others, e.g. page, note,
annotator). Rows with an empty status are not annotated yet and are skipped. Statuses:
present / partial / missing / not_applicable (aliases: yes, no, n/a, na).

Reported: exact agreement (the exit criterion: >= 80%), Cohen's kappa (SCOPE.md target
>= 0.6), a confusion matrix, and agreement per item and per group.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from app.schemas.repro import Checklist, Scorecard

LABELS = ("present", "partial", "missing", "not_applicable")
ALIASES = {
    "yes": "present",
    "y": "present",
    "no": "missing",
    "n": "missing",
    "n/a": "not_applicable",
    "na": "not_applicable",
    "not applicable": "not_applicable",
}

GOLD_COLUMNS = ["paper_id", "item_id", "group", "description", "status", "page", "note"]


def normalize_status(raw: str) -> str | None:
    s = raw.strip().lower().replace("-", "_")
    s = ALIASES.get(s, s)
    return s if s in LABELS else None


def load_gold(path: Path) -> dict[tuple[str, str], str]:
    """(paper_id, item_id) -> status. Raises on an unknown status, so typos surface."""
    gold: dict[tuple[str, str], str] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            raw = (row.get("status") or "").strip()
            if not raw:
                continue
            status = normalize_status(raw)
            if status is None:
                raise ValueError(f"{path}:{n}: unknown status {raw!r} (use {', '.join(LABELS)})")
            gold[(row["paper_id"].strip(), row["item_id"].strip())] = status
    return gold


def write_template(path: Path, paper_ids: list[str], checklist: Checklist) -> None:
    """An empty annotation sheet: one row per paper x checklist item."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(GOLD_COLUMNS)
        for pid in paper_ids:
            for item in checklist.items:
                writer.writerow([pid, item.id, item.group, item.description, "", "", ""])


@dataclass
class Agreement:
    compared: int = 0
    agreed: int = 0
    kappa: float | None = None
    confusion: Counter[tuple[str, str]] = field(default_factory=Counter)  # (gold, system)
    per_item: dict[str, tuple[int, int]] = field(default_factory=dict)  # id -> (agreed, total)
    per_group: dict[str, tuple[int, int]] = field(default_factory=dict)
    disagreements: list[tuple[str, str, str, str]] = field(default_factory=list)
    papers_annotated: set[str] = field(default_factory=set)

    @property
    def rate(self) -> float | None:
        return self.agreed / self.compared if self.compared else None


def compare(cards: dict[str, Scorecard], gold: dict[tuple[str, str], str]) -> Agreement:
    """System "unknown" counts as a disagreement: the checker could not decide it."""
    out = Agreement()
    pairs: list[tuple[str, str]] = []
    item_tot: Counter[str] = Counter()
    item_ok: Counter[str] = Counter()
    group_tot: Counter[str] = Counter()
    group_ok: Counter[str] = Counter()
    for pid, card in cards.items():
        for item in card.items:
            g = gold.get((pid, item.id))
            if g is None:
                continue
            out.papers_annotated.add(pid)
            sys_status = item.status
            pairs.append((g, sys_status))
            out.confusion[(g, sys_status)] += 1
            ok = g == sys_status
            item_tot[item.id] += 1
            group_tot[item.group] += 1
            if ok:
                item_ok[item.id] += 1
                group_ok[item.group] += 1
            else:
                out.disagreements.append((pid, item.id, g, sys_status))
    out.compared = len(pairs)
    out.agreed = sum(1 for g, s in pairs if g == s)
    out.kappa = cohen_kappa(pairs)
    out.per_item = {k: (item_ok[k], v) for k, v in item_tot.items()}
    out.per_group = {k: (group_ok[k], v) for k, v in group_tot.items()}
    return out


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    n = len(pairs)
    if not n:
        return None
    observed = sum(1 for a, b in pairs if a == b) / n
    gold = Counter(a for a, _ in pairs)
    system = Counter(b for _, b in pairs)
    expected = sum(gold[k] * system[k] for k in set(gold) | set(system)) / (n * n)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return round((observed - expected) / (1 - expected), 3)
