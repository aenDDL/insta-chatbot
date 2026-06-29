from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Request, WebSocket
from fastapi.templating import Jinja2Templates

from app.domain.agent import AgentService, pass_to_agent

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/api/v1")


@router.get("/")
async def chat_ui(request: Request):
    return templates.TemplateResponse(request, "layout.html")


@router.websocket("/ws/agent")
@inject
async def agent_ws(
    ws: WebSocket,
    service: FromDishka[AgentService],
):
    await ws.accept()
    while True:
        prompt = await ws.receive_text()
        async for chunk in pass_to_agent(service, prompt):
            await ws.send_text(f"{chunk}")
