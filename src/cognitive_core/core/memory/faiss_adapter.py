from __future__ import annotations

"""Simplified FAISS adapter used for tests."""

from collections import Counter
import heapq
import math
import re
from typing import List, Tuple

from .base import MemoryAdapter


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _embed(text: str) -> Counter[str]:
    """Create a naive bag-of-words embedding."""

    tokens = _TOKEN_RE.findall(text.lower())
    return Counter(tokens)


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    """Compute cosine similarity between two bag-of-words vectors."""
    intersection = set(a) & set(b)
    dot = sum(a[token] * b[token] for token in intersection)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class FaissMemoryAdapter(MemoryAdapter):
    """In-memory implementation mimicking a FAISS vector store."""

    def __init__(self) -> None:
        self._store: List[Tuple[Counter[str], str]] = []

    def save(self, text: str) -> None:
        self._store.append((_embed(text), text))

    def retrieve(self, query: str, top_k: int = 1) -> List[str]:
        query_emb = _embed(query)
        if not self._store or top_k <= 0:
            return []

        scored = (
            (_cosine(query_emb, embedding), text)
            for embedding, text in self._store
        )
        top_results = heapq.nlargest(top_k, scored, key=lambda item: item[0])
        return [text for _, text in top_results]
