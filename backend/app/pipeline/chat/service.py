"""Grounded chat (M11): retrieve passages, ask the LLM, keep only answers that cite them.

1. Hybrid search over the paper's passages (retrieval/search.py). Nothing relevant: refuse
   without calling the LLM.
2. One LLM call with the top passages, labelled [P1]..[Pk] (short markers are copied far more
   reliably than chunk ids).
3. Python checks the answer: markers that do not exist are removed; an "answerable" answer
   with no valid citation is refused, because it is not grounded in the paper.
"""

from __future__ import annotations

import re

from app import prompts
from app.config import Settings
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.pipeline.retrieval.embedder import Embedder
from app.pipeline.retrieval.search import PaperIndex
from app.schemas.chat import ChatAnswer, ChatOut, ChatRequest, Citation, Retrieved

_MARKER = re.compile(r"\[(P\d+)\]")
NOT_FOUND = "I could not find this in the paper."


def answer(
    request: ChatRequest,
    index: PaperIndex,
    embedder: Embedder | None,
    client: LLMClient,
    settings: Settings,
) -> ChatAnswer:
    cfg = settings.chat
    mode = "hybrid" if embedder is not None and index.vectors is not None else "bm25"
    history = request.history[-2 * cfg.history_turns :]
    # A follow-up ("and the batch size?") is searched together with the previous question.
    last_question = next((t.content for t in reversed(history) if t.role == "user"), "")
    query = (
        f"{request.question} {last_question}".strip()
        if len(request.question) < 60
        else request.question
    )
    hits = index.search(
        query, embedder, k=cfg.top_k, candidates=cfg.candidates, min_cosine=cfg.min_cosine
    )
    retrieved = [
        Retrieved(chunk_id=h.passage.chunk_id, page=h.passage.page, section=h.passage.section,
                  score=round(h.score, 5), bm25=round(h.bm25, 3),
                  cosine=round(h.cosine, 3) if h.cosine is not None else None)
        for h in hits
    ]  # fmt: skip
    if not hits:
        return ChatAnswer(answer=NOT_FOUND, answered=False, retrieval=mode)

    markers = {f"P{i}": h.passage for i, h in enumerate(hits, 1)}
    prompt = prompts.render(
        "chat_answer",
        question=request.question,
        history=[t.model_dump() for t in history],
        passages=[
            {"marker": m, "section": p.section or "?", "page": p.page, "text": p.text[:1500]}
            for m, p in markers.items()
        ],
    )
    base = ChatAnswer(answer="", answered=False, retrieved=retrieved, retrieval=mode,
                      prompt_version=prompt.id)  # fmt: skip
    try:
        result = client.generate_json(prompt, ChatOut, role="extraction")
    except LLMError as exc:
        base.answer = f"The model could not answer right now ({type(exc).__name__}). Try again."
        return base
    base.provider, base.model = result.meta.provider, result.meta.model
    out = result.value

    cited = [m for m in dict.fromkeys(_MARKER.findall(out.answer)) if m in markers]
    # Remove markers the model invented: they point at nothing the reader can check.
    text = _MARKER.sub(lambda m: m.group(0) if m.group(1) in markers else "", out.answer)
    text = re.sub(r"[ \t]+([.,;:])", r"\1", re.sub(r"[ \t]{2,}", " ", text)).strip()
    if not out.answerable:
        base.answer = text or NOT_FOUND
        return base
    if not cited:
        base.answer = NOT_FOUND + " (The model answered without citing the paper.)"
        return base
    base.answer, base.answered = text, True
    base.citations = [
        Citation(marker=m, chunk_id=markers[m].chunk_id, page=markers[m].page,
                 section=markers[m].section, text=markers[m].text[:600], boxes=markers[m].boxes)
        for m in cited
    ]  # fmt: skip
    return base
