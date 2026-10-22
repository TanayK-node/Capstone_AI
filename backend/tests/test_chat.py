"""Retrieval and grounded chat (M11)."""

import random

from app.config import Settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.llm.types import ProviderRequest, ProviderResponse
from app.pipeline.chat.service import NOT_FOUND, answer
from app.pipeline.retrieval.search import PaperIndex, Passage, tokenize
from app.schemas.chat import ChatRequest, ChatTurn
from tests.conftest import FakeClock, FakeEmbedder

PASSAGES = [
    Passage("c1", "We train with Adam using a learning rate of 3e-4 for 50k steps.", 4, "Setup"),
    Passage("c2", "Training took about 36 hours on 8 NVIDIA A100 GPUs.", 4, "Setup"),
    Passage("c3", "On FLORES-200 the model improves BLEU by 2.1 points.", 5, "Results"),
    Passage(
        "c4", "We only evaluate translation; long documents may behave differently.", 6, "Limits"
    ),
]


def index(with_vectors: bool = True) -> PaperIndex:
    emb = FakeEmbedder()
    vectors = emb.embed([p.text for p in PASSAGES]) if with_vectors else None
    return PaperIndex(PASSAGES, vectors)


def test_tokenize_keeps_numbers_and_names() -> None:
    assert tokenize("What is the learning-rate of FLORES-200 in 3e-4?") == [
        "learning-rate", "flores-200", "3e-4"
    ]  # fmt: skip


def test_hybrid_and_bm25_search() -> None:
    hits = index().search("which optimizer and learning rate", FakeEmbedder(), k=2)
    assert hits[0].passage.chunk_id == "c1" and hits[0].cosine is not None
    bm25_only = index(with_vectors=False).search("A100 GPUs", None, k=1)
    assert bm25_only[0].passage.chunk_id == "c2" and bm25_only[0].cosine is None


def test_off_topic_question_finds_nothing() -> None:
    assert index().search("who won the football world cup", FakeEmbedder()) == []


class ScriptedChat:
    name = "gemini"

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.calls: list[ProviderRequest] = []

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self.calls.append(request)
        return ProviderResponse(self.reply)


def ask(settings: Settings, reply: str, question: str, history=None):  # type: ignore[no-untyped-def]
    clock = FakeClock()
    provider = ScriptedChat(reply)
    llm = LLMClient(settings, {"gemini": provider}, MemoryCache(), clock=clock,  # type: ignore[dict-item]
                    sleep=clock.sleep, rng=random.Random(0))  # fmt: skip
    req = ChatRequest(question=question, history=history or [])
    return answer(req, index(), FakeEmbedder(), llm, settings), provider


def test_answer_keeps_valid_citations_only(settings: Settings) -> None:
    reply = '{"answerable": true, "answer": "They use Adam with lr 3e-4 [P1] [P7]."}'
    out, provider = ask(settings, reply, "Which optimizer and learning rate?")
    assert out.answered and out.answer == "They use Adam with lr 3e-4 [P1]."
    assert [c.chunk_id for c in out.citations] == ["c1"] and out.citations[0].page == 4
    assert "[P1]" in provider.calls[0].prompt and "(Setup, page 4)" in provider.calls[0].prompt


def test_uncited_answer_is_refused(settings: Settings) -> None:
    out, _ = ask(settings, '{"answerable": true, "answer": "They use Adam."}', "Which optimizer?")
    assert not out.answered and out.answer.startswith(NOT_FOUND)


def test_follow_up_is_searched_with_the_previous_question(settings: Settings) -> None:
    history = [ChatTurn(role="user", content="How long did training take on the GPUs?"),
               ChatTurn(role="assistant", content="About 36 hours [P1].")]  # fmt: skip
    reply = '{"answerable": true, "answer": "8 NVIDIA A100 GPUs [P1]."}'
    out, provider = ask(settings, reply, "and which ones?", history)
    assert out.retrieved[0].chunk_id == "c2"
    assert "user: How long did training take" in provider.calls[0].prompt


def test_off_topic_question_is_refused_without_calling_the_llm(settings: Settings) -> None:
    out, provider = ask(settings, "{}", "Who won the football world cup?")
    assert not out.answered and out.answer == NOT_FOUND and provider.calls == []


def test_word_forms_meet_in_keyword_search() -> None:
    forms = "problems problem optimizes optimized optimizing losses loss studies study"
    assert tokenize(forms) == ["problem"] * 2 + ["optimiz"] * 3 + ["loss"] * 2 + ["study"] * 2
    assert tokenize("lr 1e-4 BLEU-4 v1.1") == ["lr", "1e-4", "bleu-4", "v1.1"]  # left alone
    texts = ["These problems remain open.", "We train for 3 days.", "Results are in Table 2."]
    index = PaperIndex([Passage(f"c{i}", t, 1, "Intro") for i, t in enumerate(texts)], None)
    assert [h.passage.chunk_id for h in index.search("What problem is addressed?", None)] == ["c0"]
