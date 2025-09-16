from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, List, Optional, Sequence


class Layer(Enum):
    ROLE = "ROLE"
    GOAL = "GOAL"
    CONTEXT = "CONTEXT"
    EXAMPLES = "EXAMPLES"


class ConflictScanner:
    """Detects conflicting instructions using regex patterns and an optional LLM."""

    def __init__(
        self,
        patterns: Optional[Iterable[str]] = None,
        llm_checker: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self._regexes = [re.compile(p, re.IGNORECASE) for p in patterns or []]
        self._llm_checker = llm_checker

    def has_conflict(self, text: str) -> bool:
        for regex in self._regexes:
            if regex.search(text):
                return True
        if self._llm_checker:
            try:
                return bool(self._llm_checker(text))
            except Exception:
                return False
        return False

    def scan(self, text: str) -> None:
        if self.has_conflict(text):
            raise ValueError("Prompt conflict detected")


@dataclass
class EPaUp:
    """Composable prompt with ROLE, GOAL, CONTEXT and EXAMPLES layers."""

    role: str
    goal: str
    context: str = ""
    examples: Sequence[str] = field(default_factory=list)
    conflict_scanner: Optional[ConflictScanner] = None

    def build(self) -> str:
        parts: List[str] = [f"Role: {self.role}", f"Goal: {self.goal}"]
        if self.context:
            parts.append(f"Context: {self.context}")
        if self.examples:
            ex_lines = "\n".join(f"- {e}" for e in self.examples)
            parts.append(f"Examples:\n{ex_lines}")
        prompt = "\n".join(parts)
        if self.conflict_scanner:
            self.conflict_scanner.scan(prompt)
        return prompt

    def with_theory_of_mind(self, audience: str) -> str:
        base = self.build()
        tom_line = f"Consider what {audience} might believe, know, or intend when responding."
        return f"{base}\n{tom_line}"


__all__ = ["Layer", "ConflictScanner", "EPaUp"]
