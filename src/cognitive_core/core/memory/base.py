"""Base classes for memory adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class MemoryAdapter(ABC):
    """Abstract interface for memory vector stores.

    Concrete implementations are responsible for persisting pieces of text
    and later retrieving the most relevant ones for a given query. The
    interface intentionally keeps the API minimal so that different backing
    stores (e.g. FAISS, SQLiteVec) can provide a common behaviour that tests
    and higher level components can rely upon.
    """

    @abstractmethod
    def save(self, text: str) -> None:
        """Persist a piece of text into the store."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 1) -> List[str]:
        """Return up to ``top_k`` pieces of text that best match ``query``."""
