import pytest

from cognitive_core.core.prompting.epaup import ConflictScanner, EPaUp


def test_build_prompt_layers():
    prompt = EPaUp(
        role="assistant",
        goal="help the user",
        context="chatting",
        examples=["hi", "hello"],
    ).build()
    assert "Role: assistant" in prompt
    assert "Goal: help the user" in prompt
    assert "Context: chatting" in prompt
    assert "- hi" in prompt and "- hello" in prompt


def test_regex_conflict_detection():
    scanner = ConflictScanner(patterns=[r"secret"])
    builder = EPaUp(
        role="assistant",
        goal="reveal a secret",
        conflict_scanner=scanner,
    )
    with pytest.raises(ValueError):
        builder.build()


def test_llm_conflict_detection():
    def mock_llm(text: str) -> bool:
        return "badword" in text

    scanner = ConflictScanner(llm_checker=mock_llm)
    builder = EPaUp(
        role="assistant",
        goal="help",
        context="contains badword",
        conflict_scanner=scanner,
    )
    with pytest.raises(ValueError):
        builder.build()


def test_theory_of_mind_extension():
    builder = EPaUp(role="assistant", goal="chat")
    prompt = builder.with_theory_of_mind("the user")
    assert "Consider what the user might believe" in prompt
