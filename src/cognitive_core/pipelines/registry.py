from __future__ import annotations

"""In-memory registry of pipelines available to the CLI and API layers."""

from typing import Iterable

from ..domain.pipelines import Artifact, Pipeline


_PIPELINES: dict[str, Pipeline] = {}


def register_pipeline(pipeline: Pipeline) -> None:
    """Register or replace a pipeline definition."""

    _PIPELINES[pipeline.id] = pipeline


def get_pipeline(pipeline_id: str) -> Pipeline | None:
    """Return the pipeline with the given identifier, if present."""

    return _PIPELINES.get(pipeline_id)


def iter_pipelines() -> Iterable[Pipeline]:
    """Iterate over all registered pipelines."""

    return _PIPELINES.values()


def _sample_step() -> Artifact:
    return Artifact(name="result", data=1)


register_pipeline(Pipeline(id="sample", name="Sample", steps=[_sample_step]))


def _demo_step() -> Artifact:
    """Return a simple artifact used by the demo pipeline."""

    return Artifact(name="demo", data={"message": "hello from demo"})


register_pipeline(Pipeline(id="demo", name="Demo", steps=[_demo_step]))
