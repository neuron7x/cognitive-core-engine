from __future__ import annotations

from time import time
from uuid import uuid4

from ..domain.pipelines import Artifact, Event, Pipeline, Run


class PipelineExecutor:
    """Executes pipelines synchronously."""

    def execute(self, pipeline: Pipeline) -> Run:
        run = Run(id=str(uuid4()), pipeline_id=pipeline.id, status="running")

        for step in pipeline.steps:
            step_name = getattr(step, "__name__", "step")
            run.events.append(Event(step=step_name, type="start", timestamp=time()))
            artifact = step()
            if not isinstance(artifact, Artifact):
                artifact = Artifact(name=step_name, data=artifact)
            run.artifacts.append(artifact)
            run.events.append(Event(step=step_name, type="end", timestamp=time()))

        run.status = "completed"
        return run
