from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocket

from app.domain.agent import AgentService, stream_agent

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/")
async def chat_ui(request: Request):
    return templates.TemplateResponse(request, "layout.html")


@router.websocket("/ws/agent")
@inject
async def agent_websocket_endpoint(
    websocket: WebSocket,
    service: FromDishka[AgentService],
):
    await websocket.accept()
    async for data in websocket.iter_text():
        async for chunk in stream_agent(service, data):
            await websocket.send_text(chunk)
