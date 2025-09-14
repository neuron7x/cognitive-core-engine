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
