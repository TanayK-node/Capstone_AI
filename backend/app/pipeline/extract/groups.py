"""Section groups (M4): which parts of the paper each extraction call sees.

The extractor works per group in every mode so outputs stay comparable across models
(SCOPE.md §2). Text is tagged with block ids, which the LLM cites as chunk_id.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.pipeline.extract.hints import PATTERNS
from app.schemas.document import Block, ParsedDocument

TEXT_TYPES = {"paragraph", "footnote", "caption", "equation"}

GROUP_ROLES: dict[str, set[str]] = {
    "front": {"abstract", "introduction"},
    "method": {"method", "background"},
    "experiments": {"experiments", "results", "ablation"},
    "closing": {"limitations", "conclusion", "discussion"},
}


@dataclass
class GroupText:
    name: str
    blocks: list[Block] = field(default_factory=list)
    text: str = ""
    truncated: bool = False

    @property
    def block_ids(self) -> set[str]:
        return {b.id for b in self.blocks}


def render_block(block: Block) -> str:
    if block.type == "table":
        rows = block.table.grid() if block.table else []
        grid = "\n".join(" | ".join(r) for r in rows)
        return f"[{block.id}] {block.text}\n{grid}".rstrip()
    return f"[{block.id}] {block.text}"


def _training_details(block: Block) -> bool:
    keys = ("learning_rate", "batch_size", "hardware", "compute_time", "seeds_runs", "optimizer")
    return any(PATTERNS[k].search(block.text) for k in keys)


def build_groups(doc: ParsedDocument, max_chars: int) -> dict[str, GroupText]:
    groups = {name: GroupText(name) for name in GROUP_ROLES}
    for block in doc.blocks:
        if block.type not in TEXT_TYPES and block.type != "table":
            continue
        role = block.role or ""
        if role in ("references", "acknowledgements"):
            continue
        if block.type == "table":
            # Every results table goes to the experiments call, whatever its section role:
            # GROBID sometimes drops a "Results" heading, so the tables inherit "method".
            groups["experiments"].blocks.append(block)
            continue
        for name, roles in GROUP_ROLES.items():
            if role in roles:
                groups[name].blocks.append(block)
        # Hyperparameters and compute often live in the appendix, or in a "Training"
        # subsection that the role rules file under method.
        if role in ("appendix", "method", "other") and _training_details(block):
            groups["experiments"].blocks.append(block)

    # Papers whose headings the role step could not place: fall back to position.
    if not groups["front"].blocks:
        paragraphs = [b for b in doc.blocks if b.type == "paragraph"]
        groups["front"].blocks = paragraphs[:8]
    if not groups["method"].blocks:
        groups["method"].blocks = [b for b in doc.blocks if (b.role or "") == "other"][:15]

    for group in groups.values():
        parts: list[str] = []
        used = 0
        for block in group.blocks:
            piece = render_block(block)
            if used + len(piece) > max_chars:
                group.truncated = True
                break
            parts.append(piece)
            used += len(piece) + 2
        group.blocks = group.blocks[: len(parts)]
        group.text = "\n\n".join(parts)
    return groups
