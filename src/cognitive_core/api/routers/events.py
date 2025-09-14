from __future__ import annotations

import json
import anyio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...utils.telemetry import instrument_route
from .pipelines import RUNS

router = APIRouter()


@router.get("/events/{run_id}")
@instrument_route("events_stream")
async def stream_events(run_id: str):
    async def event_generator():
        run = RUNS.get(run_id)
        if not run:
            yield 'event: end\ndata: {"error": "run_not_found"}\n\n'
            return
        for ev in run.events:
            payload = json.dumps(
                {"step": ev.step, "type": ev.type, "timestamp": ev.timestamp}
            )
            yield f"event: {ev.type}\ndata: {payload}\n\n"
            await anyio.sleep(0)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
