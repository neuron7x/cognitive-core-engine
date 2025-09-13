from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...core.pipeline_executor import PipelineExecutor
from ...domain.pipelines import Artifact, Pipeline

router = APIRouter()


# In-memory registry for demo purposes
PIPELINES: dict[str, Pipeline] = {}


def _sample_step() -> Artifact:
    return Artifact(name="result", data=1)


PIPELINES["sample"] = Pipeline(id="sample", name="Sample", steps=[_sample_step])
executor = PipelineExecutor()


class RunRequest(BaseModel):
    pipeline_id: str


@router.get("/v1/pipelines/{pipeline_id}")
def get_pipeline(pipeline_id: str):
    pipeline = PIPELINES.get(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"id": pipeline.id, "name": pipeline.name, "steps": len(pipeline.steps)}


@router.post("/v1/pipelines/run")
def run_pipeline(req: RunRequest):
    pipeline = PIPELINES.get(req.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    run = executor.execute(pipeline)
    return {
        "run_id": run.id,
        "status": run.status,
        "artifacts": [a.name for a in run.artifacts],
    }
