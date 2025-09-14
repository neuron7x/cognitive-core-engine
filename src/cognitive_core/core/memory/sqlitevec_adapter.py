from __future__ import annotations

"""Simplified SQLiteVec adapter used for tests."""

from collections import Counter
import math
from typing import List, Tuple

from .base import MemoryAdapter


def _embed(text: str) -> Counter[str]:
    """Create a naive bag-of-words embedding."""
    return Counter(text.lower().split())


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    """Compute cosine similarity between two bag-of-words vectors."""
    intersection = set(a) & set(b)
    dot = sum(a[token] * b[token] for token in intersection)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class SQLiteVecMemoryAdapter(MemoryAdapter):
    """In-memory implementation mimicking a SQLiteVec vector store."""

    def __init__(self) -> None:
        self._store: List[Tuple[Counter[str], str]] = []

    def save(self, text: str) -> None:
        self._store.append((_embed(text), text))

    def retrieve(self, query: str, top_k: int = 1) -> List[str]:
        query_emb = _embed(query)
        ranked = sorted(
            self._store,
            key=lambda item: _cosine(query_emb, item[0]),
            reverse=True,
        )
        return [text for _, text in ranked[:top_k]]
