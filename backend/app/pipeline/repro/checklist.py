"""Load the reproducibility checklist (config/checklist.yaml, next to config.yaml)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.config import config_path
from app.schemas.repro import Checklist, ChecklistGroup, ChecklistItem


def checklist_path() -> Path:
    return config_path().parent / "checklist.yaml"


@lru_cache
def load_checklist(path: Path | None = None) -> Checklist:
    raw = yaml.safe_load((path or checklist_path()).read_text(encoding="utf-8"))
    groups = [ChecklistGroup(id=k, **v) for k, v in raw["groups"].items()]
    items = [ChecklistItem.model_validate(i) for i in raw["items"]]
    unknown = {i.group for i in items} - {g.id for g in groups}
    if unknown:
        raise ValueError(f"checklist items use undefined groups: {sorted(unknown)}")
    return Checklist(version=raw["version"], groups=groups, items=items)
