from __future__ import annotations

import asyncio
import inspect
from time import time
from uuid import uuid4

from ..domain.pipelines import Artifact, Event, Pipeline, Run


class PipelineExecutor:
    """Executes pipelines synchronously or asynchronously."""

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

    async def execute_async(self, pipeline: Pipeline) -> Run:
        run = Run(id=str(uuid4()), pipeline_id=pipeline.id, status="running")

        async def run_step(step: object) -> None:
            step_name = getattr(step, "__name__", "step")
            run.events.append(Event(step=step_name, type="start", timestamp=time()))
            result = step()
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, Artifact):
                result = Artifact(name=step_name, data=result)
            run.artifacts.append(result)
            run.events.append(Event(step=step_name, type="end", timestamp=time()))

        await asyncio.gather(*(run_step(step) for step in pipeline.steps))
        run.status = "completed"
        return run
