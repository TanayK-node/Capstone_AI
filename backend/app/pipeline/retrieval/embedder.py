"""Local text embeddings (SCOPE.md: retrieval runs locally, never through the LLM API).

fastembed runs the configured model (BAAI/bge-small-en-v1.5 by default) with ONNX Runtime on
the CPU: same embeddings as sentence-transformers, without PyTorch. The model downloads from
Hugging Face once into embeddings.cache_dir. When it cannot load (offline, disabled in
config), search falls back to BM25 alone and says so.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Protocol

import numpy as np

from app.config import Settings

log = logging.getLogger("paperlens.retrieval")


class Embedder(Protocol):
    model_name: str

    def embed(self, texts: list[str], *, query: bool = False) -> np.ndarray:
        """L2-normalised float32 vectors, one row per text."""
        ...


class FastEmbedder:
    def __init__(self, model_name: str, cache_dir: Path | None, threads: int | None) -> None:
        from fastembed import TextEmbedding

        self.model_name = model_name
        self._model = TextEmbedding(
            model_name=model_name,
            cache_dir=str(cache_dir) if cache_dir else None,
            threads=threads,
        )

    def embed(self, texts: list[str], *, query: bool = False) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        # bge models expect queries prefixed with an instruction; passages are embedded as is.
        rows = self._model.query_embed(texts) if query else self._model.passage_embed(texts)
        vectors = np.asarray(list(rows), dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        normalised: np.ndarray = vectors / np.maximum(norms, 1e-12)
        return normalised


_cache: dict[str, Embedder | None] = {}
_lock = threading.Lock()


def get_embedder(settings: Settings) -> Embedder | None:
    """The configured embedder, loaded once per process; None if disabled or unavailable."""
    cfg = settings.embeddings
    if not cfg.enabled:
        return None
    with _lock:
        if cfg.model not in _cache:
            try:
                cache_dir = Path(settings.app.data_dir) / "models"
                _cache[cfg.model] = FastEmbedder(cfg.model, cache_dir, cfg.threads)
            except Exception as exc:  # offline, blocked download, missing runtime
                log.warning("embedding model %s unavailable (%s): BM25 only", cfg.model, exc)
                _cache[cfg.model] = None
        return _cache[cfg.model]


def to_bytes(vectors: np.ndarray) -> bytes:
    return np.ascontiguousarray(vectors, dtype=np.float32).tobytes()


def from_bytes(data: bytes, dim: int) -> np.ndarray:
    return np.frombuffer(data, dtype=np.float32).reshape(-1, dim)
