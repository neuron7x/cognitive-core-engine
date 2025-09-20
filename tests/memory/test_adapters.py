import pytest

from cognitive_core.core.memory.faiss_adapter import FaissMemoryAdapter
from cognitive_core.core.memory.sqlitevec_adapter import SQLiteVecMemoryAdapter


@pytest.mark.parametrize("adapter_cls", [FaissMemoryAdapter, SQLiteVecMemoryAdapter])
def test_auto_context_selection(adapter_cls) -> None:
    """Saving and retrieving selects the most relevant context automatically."""

    adapter = adapter_cls()
    adapter.save("Paris is the capital of France")
    adapter.save("Berlin is the capital of Germany")
    adapter.save("Rome is the capital of Italy")

    results = adapter.retrieve("What is the capital of Germany?")
    assert results[0] == "Berlin is the capital of Germany"


@pytest.mark.parametrize("adapter_cls", [FaissMemoryAdapter, SQLiteVecMemoryAdapter])
def test_retrieve_respects_top_k_ordering(adapter_cls) -> None:
    """Retrieval returns entries sorted by similarity and respects top_k."""

    adapter = adapter_cls()
    docs = [
        "red blue blue blue",
        "red blue green",
        "red",
        "green green green",
    ]
    for doc in docs:
        adapter.save(doc)

    # Top-3 results should be ordered by cosine similarity.
    results = adapter.retrieve("red blue", top_k=3)
    assert results == docs[:3]

    # Requesting more than available returns all documents in ranked order.
    all_results = adapter.retrieve("red blue", top_k=10)
    assert all_results == docs


@pytest.mark.parametrize("adapter_cls", [FaissMemoryAdapter, SQLiteVecMemoryAdapter])
def test_retrieve_handles_small_top_k(adapter_cls) -> None:
    """Retrieving with non-positive top_k yields an empty result."""

    adapter = adapter_cls()
    adapter.save("foo bar baz")

    assert adapter.retrieve("foo", top_k=0) == []
    assert adapter.retrieve("foo", top_k=-5) == []
