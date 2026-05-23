from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.api.v1.router import router as v1_router
from app.agents_runner.stream import stream_graph_workflow


class AgentQueryRequest(BaseModel):
    query: str
    session_id: str = "default"


api_router = APIRouter()

api_router.include_router(
    v1_router,
    prefix="/api/v1"
)


@api_router.post("/agent/query")
async def agent_query(request: AgentQueryRequest):
    """Multi-agent workflow — streams intermediate steps + final answer."""
    async def event_generator():
        async for chunk in stream_graph_workflow(request.query, request.session_id):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")
