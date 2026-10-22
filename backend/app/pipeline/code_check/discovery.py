"""Find the paper's own repository (M7 repo discovery).

1. Links in the paper text (extraction.code_urls, found by regex), ranked: a sentence like
   "our code is available at ..." and a repo named like the method score up; a link in
   "we use the implementation in the X library" scores down (someone else's code).
2. GitHub search by title (GitHub API), only when the paper links nothing; a guess, so it
   needs the user's confirmation below CONFIRM_BELOW.
3. A repository the user confirmed or typed (POST /api/papers/{id}/code/confirm) wins.
"""

from __future__ import annotations

import re

from rapidfuzz import fuzz

from app.pipeline.code_check.clone import split_url
from app.schemas.code import RepoCandidate
from app.schemas.extraction import PaperExtraction

CONFIRM_BELOW = 0.6

_OWN = re.compile(
    r"\b(our|the) (source )?(code|implementation|models?|weights)\b.{0,60}\b(available|released?|"
    r"open[- ]sourced?|public)|\bavailable at\b|\bwe (release|open[- ]source|make)\b|"
    r"\brelease[ds]? (our|the) (source )?(code|models?|implementation)|"
    r"\bcode (is|can be found|will be)",
    re.I,
)
# Someone else's code. Narrow on purpose: "The code we used to train ... is available at"
# (Transformer) is the authors' own, "Our implementation is based on the ... in X" (ViT) is not.
_THIRD_PARTY = re.compile(
    r"\bwe (use|used|adopt|adopted|build on|follow|followed) (the|an?|their|existing|publicly)\b|"
    r"\bbased on (the|an?|their)\b|\b(library|toolkit)\b|\bimplementation (in|of|from)\b",
    re.I,
)


def candidates_from_paper(
    extraction: PaperExtraction, method_names: list[str]
) -> list[RepoCandidate]:
    out: list[RepoCandidate] = []
    title = (extraction.metadata.title or "").lower()
    for item in extraction.code_urls:
        url = item.value
        base, subdir = split_url(url)
        sentence = item.evidence[0].quote if item.evidence else ""
        repo_name = base.rstrip("/").split("/")[-1].lower()
        score, reasons = 0.5, ["linked in the paper"]
        if _OWN.search(sentence):
            score += 0.3
            reasons.append("the sentence says the code is the authors'")
        if _THIRD_PARTY.search(sentence):
            score -= 0.4
            reasons.append("the sentence describes code the authors built on, not theirs")
        names = [n.lower() for n in method_names] + ([title] if title else [])
        if any(fuzz.partial_ratio(repo_name, n) >= 80 for n in names if n):
            score += 0.2
            reasons.append(f"repository name '{repo_name}' matches the method")
        if "huggingface.co" in base and "/spaces/" not in url:
            score -= 0.2  # a model card, not code
            reasons.append("a Hugging Face model page, not a code repository")
        out.append(
            RepoCandidate(
                url=url,
                source="paper",
                confidence=round(min(1.0, max(0.0, score)), 2),
                reason="; ".join(reasons),
                subdir=subdir,
            )
        )
    out.sort(key=lambda c: c.confidence, reverse=True)
    return out


def candidates_from_search(results: list[dict[str, object]], title: str) -> list[RepoCandidate]:
    """GitHub search results -> candidates scored by how well the repo matches the title."""
    out: list[RepoCandidate] = []
    for r in results[:5]:
        name = str(r.get("full_name", ""))
        desc = str(r.get("description") or "")
        sim = max(fuzz.token_set_ratio(title, desc), fuzz.partial_ratio(name.split("/")[-1], title))
        out.append(
            RepoCandidate(
                url=str(r.get("html_url", f"https://github.com/{name}")),
                source="github_search",
                confidence=round(0.5 * sim / 100, 2),  # never above 0.5: always confirm
                reason=(
                    f"GitHub search by title ({sim:.0f}% match, "
                    f"{r.get('stargazers_count', 0)} stars)"
                ),
            )
        )
    out.sort(key=lambda c: c.confidence, reverse=True)
    return out
