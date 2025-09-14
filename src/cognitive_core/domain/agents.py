from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class Role:
    """Represents a debating role executed by an agent."""

    name: str
    system_prompt: str


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for a single debating agent."""

    role: Role
    model: str = "mock"


@dataclass
class DebateRound:
    """Container for the result of running a prompt through multiple roles."""

    prompt: str
    responses: Dict[str, str] = field(default_factory=dict)
