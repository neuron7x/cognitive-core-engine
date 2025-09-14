from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...core.pipeline_executor import PipelineExecutor
from ...domain.pipelines import Artifact, Pipeline
from ...plugins import dispatch
from ...plugins.plugin_loader import load_plugins
from ...utils.telemetry import instrument_route, record_llm_tokens

router = APIRouter()

# Ensure plugins are loaded so pipeline stages are available
load_plugins()


# In-memory registry for demo purposes
PIPELINES: dict[str, Pipeline] = {}


def _sample_step() -> Artifact:
    return Artifact(name="result", data=1)


PIPELINES["sample"] = Pipeline(id="sample", name="Sample", steps=[_sample_step])
executor = PipelineExecutor()


class RunRequest(BaseModel):
    pipeline_id: str


@router.get("/v1/pipelines/{pipeline_id}")
@instrument_route("get_pipeline")
def get_pipeline(pipeline_id: str):
    pipeline = PIPELINES.get(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"id": pipeline.id, "name": pipeline.name, "steps": len(pipeline.steps)}


@router.post("/v1/pipelines/run")
@instrument_route("run_pipeline")
def run_pipeline(req: RunRequest):
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


class ISRRequest(BaseModel):
    text: str


@router.post("/pipelines/isr_run")
@instrument_route("isr_run")
def run_isr(req: ISRRequest):
    state = {"text": req.text}

    def r_stage() -> Artifact:
        res = dispatch("isr.r", {"text": state["text"]})
        state["text"] = res["text"]
        return Artifact(
            name="r",
            data=res["text"],
            logic=res.get("logic"),
            semantic=res.get("semantic"),
            narrative=res.get("narrative"),
        )

    def i_stage() -> Artifact:
        res = dispatch("isr.i", {"text": state["text"]})
        state["text"] = res["text"]
        return Artifact(
            name="i",
            data=res["text"],
            logic=res.get("logic"),
            semantic=res.get("semantic"),
            narrative=res.get("narrative"),
        )

    def p_stage() -> Artifact:
        res = dispatch("isr.p", {"text": state["text"]})
        state["text"] = res["text"]
        return Artifact(
            name="p",
            data=res["text"],
            logic=res.get("logic"),
            semantic=res.get("semantic"),
            narrative=res.get("narrative"),
        )

    def omega_stage() -> Artifact:
        res = dispatch("isr.omega", {"text": state["text"]})
        state["text"] = res["text"]
        return Artifact(
            name="omega",
            data=res["text"],
            logic=res.get("logic"),
            semantic=res.get("semantic"),
            narrative=res.get("narrative"),
        )

    pipeline = Pipeline(id="isr", name="ISR", steps=[r_stage, i_stage, p_stage, omega_stage])
    run = executor.execute(pipeline)
    record_llm_tokens("isr_run", len(run.artifacts))
    return {
        "run_id": run.id,
        "status": run.status,
        "output": state["text"],
        "artifacts": [
            {
                "name": a.name,
                "data": a.data,
                "logic": a.logic,
                "semantic": a.semantic,
                "narrative": a.narrative,
            }
            for a in run.artifacts
        ],
    }
