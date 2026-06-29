from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.adapters.instagram_auth import InstagramLoginService
from app.api.dependencies import (
    ProvideAdapters,
    ProvideInstagram,
    ProvideXai,
    provide_service,
)
from app.api.v1 import agent
from app.infrastructure.logger import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with container() as c:
        instagram = await c.get(InstagramLoginService)
        await instagram.login()
    yield
    await app.state.dishka_container.close()


container = make_async_container(
    provide_service(),
    ProvideInstagram(),
    ProvideXai(),
    ProvideAdapters(),
)


app = FastAPI(lifespan=lifespan)

setup_dishka(container, app)

app.include_router(agent.router)
