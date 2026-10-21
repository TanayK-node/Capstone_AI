"""Section role classification (M3): heuristics first, one small LLM call for the rest."""

from __future__ import annotations

import logging
import re
from typing import get_args

from pydantic import BaseModel, Field

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.schemas.document import SectionRole

log = logging.getLogger("paperlens.structure")

ROLES: tuple[str, ...] = get_args(SectionRole)

# Order matters: the first match wins ("Experimental results" -> results, not experiments).
_RULE_SOURCE: list[tuple[SectionRole, str]] = [
    ("abstract", r"^abstract$"),
    ("references", r"^(references|bibliography|works cited|literature cited)$"),
    ("acknowledgements", r"^acknowledge?ments?$"),
    ("appendix", r"^(appendix|appendices|supplementary|supplemental)"),
    ("ablation", r"ablation"),
    ("limitations", r"limitation|threats to validity|broader impact|ethic"),
    ("related_work", r"related work|prior work|previous work|literature review"),
    ("introduction", r"^(introduction|overview|motivation)$"),
    ("background", r"background|preliminar|problem (setup|setting|formulation|definition)"),
    ("results", r"results|findings|main (results|comparison)|comparison with|performance"),
    (
        "experiments",
        r"experiment|evaluation|empirical|setup|implementation details|training details|"
        r"datasets?|benchmarks?|baselines",
    ),
    ("discussion", r"discussion|analysis|case stud|error analysis|qualitative"),
    ("conclusion", r"conclu|summary|future work|closing remarks"),
    (
        "method",
        r"method|approach|model|architecture|framework|proposed|our|algorithm|technique|"
        r"formulation|design|objective|training$",
    ),
]
_RULES = [(role, re.compile(p, re.IGNORECASE)) for role, p in _RULE_SOURCE]
_NUMBER = re.compile(r"^(?:[A-Z]|\d+)(?:\.\d+)*\.?\s+")
# Roles a subsection may claim on its own; otherwise it inherits its parent's role.
CHILD_OVERRIDES = {"ablation", "results", "limitations", "discussion"}


def strip_number(heading: str) -> str:
    return _NUMBER.sub("", heading).strip()


def classify_heading(heading: str) -> SectionRole | None:
    title = strip_number(heading)
    for role, pattern in _RULES:
        if pattern.search(title):
            return role
    return None


def is_appendix_number(heading: str) -> bool:
    """'A Proofs', 'B.2 Hyperparameters': letter-numbered sections are appendices."""
    return bool(re.match(r"^[A-Z](?:\.\d+)*\.?\s+\S", heading))


class _RoleAssignment(BaseModel):
    index: int
    role: SectionRole


class _RoleResponse(BaseModel):
    sections: list[_RoleAssignment] = Field(default_factory=list)


def classify_with_llm(
    client: LLMClient | None, headings: list[tuple[str, str]]
) -> tuple[dict[int, SectionRole], str | None]:
    """headings: (heading, first sentence). Returns index -> role and the prompt version used.

    One batched call per paper. Any failure returns {} and the caller falls back to "other".
    """
    if not headings or client is None:
        return {}, None
    prompt = prompts.render(
        "section_roles",
        roles=[r for r in ROLES if r not in ("abstract", "references")],
        sections=[
            {"index": i, "heading": h, "snippet": s[:300]} for i, (h, s) in enumerate(headings)
        ],
    )
    try:
        result = client.generate_json(prompt, _RoleResponse, role="small")
    except LLMError as exc:
        log.warning("section role LLM call failed: %s", exc)
        return {}, prompt.id
    return {a.index: a.role for a in result.value.sections if 0 <= a.index < len(headings)}, (
        prompt.id
    )
