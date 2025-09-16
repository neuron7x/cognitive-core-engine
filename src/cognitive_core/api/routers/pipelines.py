from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from ...core.agents_router import AgentsRouter
from ...core.pipeline_executor import PipelineExecutor
from ...domain.agents import DebateRound
from ...domain.pipelines import Artifact, Pipeline
from ...utils.telemetry import instrument_route, record_llm_tokens

router = APIRouter()


# In-memory registry for demo purposes
PIPELINES: dict[str, Pipeline] = {}


def _sample_step() -> Artifact:
    return Artifact(name="result", data=1)


PIPELINES["sample"] = Pipeline(id="sample", name="Sample", steps=[_sample_step])
executor = PipelineExecutor()
agents_router = AgentsRouter()


class RunRequest(BaseModel):
    pipeline_id: str


class DebateRequest(BaseModel):
    prompt: str
    roles: list[str]
    concurrent: bool = False


RunRequest.model_rebuild()
DebateRequest.model_rebuild()


@router.get("/v1/pipelines/{pipeline_id}")
@instrument_route("get_pipeline")
def get_pipeline(pipeline_id: str):
    pipeline = PIPELINES.get(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"id": pipeline.id, "name": pipeline.name, "steps": len(pipeline.steps)}


@router.post("/v1/pipelines/run")
@instrument_route("run_pipeline")
def run_pipeline(req: RunRequest = Body(...)):
    pipeline = PIPELINES.get(req.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    run = executor.execute(pipeline)
    record_llm_tokens("run_pipeline", len(run.artifacts))
    return {
        "run_id": run.id,
        "status": run.status,
        "artifacts": [a.name for a in run.artifacts],
    }


@router.post("/pipelines/aots_debate")
@instrument_route("aots_debate")
def aots_debate(req: DebateRequest) -> DebateRound:
    round = agents_router.run(req.prompt, req.roles, concurrent=req.concurrent)
    record_llm_tokens("aots_debate", len(round.responses))
    return round
