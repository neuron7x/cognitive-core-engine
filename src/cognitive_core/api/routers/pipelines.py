from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.agents_router import AgentsRouter
from ...database import SessionLocal, get_session, init_db
from ...domain.agents import DebateRound
from ...services.pipelines import (
    PipelineAlreadyExistsError,
    PipelineNotFoundError,
    PipelineService,
)
from ...utils.telemetry import instrument_route, record_llm_tokens

router = APIRouter()
agents_router = AgentsRouter()

init_db()


def _seed_default_pipeline() -> None:
    with SessionLocal() as session:
        service = PipelineService(session)
        try:
            service.create_pipeline("Sample")
        except PipelineAlreadyExistsError:
            session.rollback()


_seed_default_pipeline()


class PipelineCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)


class RunRequest(BaseModel):
    pipeline_id: int


class DebateRequest(BaseModel):
    prompt: str
    roles: list[str]
    concurrent: bool = False


PipelineCreateRequest.model_rebuild()
RunRequest.model_rebuild()
DebateRequest.model_rebuild()


def _get_service(session: Session = Depends(get_session)) -> PipelineService:
    return PipelineService(session)


@router.get("/v1/pipelines")
@instrument_route("list_pipelines")
def list_pipelines(service: PipelineService = Depends(_get_service)):
    pipelines = service.list_pipelines()
    return [
        {"id": pipeline.id, "name": pipeline.name, "steps": service.step_count(pipeline)}
        for pipeline in pipelines
    ]


@router.post("/v1/pipelines", status_code=status.HTTP_201_CREATED)
@instrument_route("create_pipeline")
def create_pipeline(
    req: PipelineCreateRequest, service: PipelineService = Depends(_get_service)
):
    try:
        pipeline = service.create_pipeline(req.name)
    except PipelineAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Pipeline already exists")
    return {"id": pipeline.id, "name": pipeline.name, "steps": service.step_count(pipeline)}


@router.get("/v1/pipelines/{pipeline_id}")
@instrument_route("get_pipeline")
def get_pipeline(pipeline_id: int, service: PipelineService = Depends(_get_service)):
    try:
        pipeline = service.get_pipeline(pipeline_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Pipeline not found") from exc
    return {"id": pipeline.id, "name": pipeline.name, "steps": service.step_count(pipeline)}


@router.post("/v1/pipelines/run")
@instrument_route("run_pipeline")
def run_pipeline(req: RunRequest = Body(...), service: PipelineService = Depends(_get_service)):
    try:
        run_model, run = service.run_pipeline(req.pipeline_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Pipeline not found") from exc
    record_llm_tokens("run_pipeline", len(run.artifacts))
    return {
        "run_id": run_model.id,
        "status": run_model.status,
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
