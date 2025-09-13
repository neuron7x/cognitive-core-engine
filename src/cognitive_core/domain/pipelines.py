from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, List, Union


@dataclass(frozen=True)
class Artifact:
    """Materialized result produced by a pipeline step."""

    name: str
    data: Any


@dataclass(frozen=True)
class Event:
    """Represents lifecycle events during a pipeline run."""

    step: str
    type: str
    timestamp: float


@dataclass
class Run:
    """Execution state of a pipeline."""

    id: str
    pipeline_id: str
    status: str
    events: List[Event] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)


Step = Union[Callable[[], Any], Callable[[], Awaitable[Any]]]


@dataclass(frozen=True)
class Pipeline:
    """A pipeline whose steps may be synchronous or asynchronous."""

    id: str
    name: str
    steps: List[Step]
