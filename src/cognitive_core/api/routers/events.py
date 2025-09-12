import anyio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

async def sse_gen():
    for i in range(1, 6):
        yield f"event: tick\ndata: {{\"step\": {i}}}\n\n"
        await anyio.sleep(0.2)

@router.get("/sse")
async def sse():
    return StreamingResponse(sse_gen(), media_type="text/event-stream")
