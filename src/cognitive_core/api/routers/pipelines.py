from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from ...core.agents_router import AgentsRouter
from ...core.pipeline_executor import PipelineExecutor
from ...domain.agents import DebateRound
from ...utils.telemetry import instrument_route, record_llm_tokens
from ...pipelines import registry as pipeline_registry

router = APIRouter()


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
def get_pipeline_route(pipeline_id: str):
    pipeline = pipeline_registry.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"id": pipeline.id, "name": pipeline.name, "steps": len(pipeline.steps)}


@router.post("/v1/pipelines/run")
@instrument_route("run_pipeline")
def run_pipeline(req: RunRequest = Body(...)):
    pipeline = pipeline_registry.get_pipeline(req.pipeline_id)
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
    try:
        round = agents_router.run(req.prompt, req.roles, concurrent=req.concurrent)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    record_llm_tokens("aots_debate", len(round.responses))
    return round
