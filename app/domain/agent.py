from dataclasses import dataclass
from enum import StrEnum, auto

from pydantic_ai import Agent, RunContext

from app.domain.ports import InstagramPort


@dataclass
class AgentDependencies:
    instagram: InstagramPort


@dataclass
class AgentService:
    agent: Agent
    deps: AgentDependencies


class InstagramAction(StrEnum):
    send_message = auto()
    follow_user = auto()
    like_post = auto()


async def send_message(
    ctx: RunContext[AgentDependencies], message: str, username: str
) -> None:
    await ctx.deps.instagram.send_message(message, username)


async def follow_user(ctx: RunContext[AgentDependencies], user_id: int) -> None:

    await ctx.deps.instagram.follow_user(user_id)


async def like_post(ctx: RunContext[AgentDependencies], post_id: int) -> None:
    await ctx.deps.instagram.like_post(post_id)


async def pass_to_agent(service: AgentService, prompt: str):
    async with service.agent.run_stream(user_prompt=prompt, deps=service.deps) as run:
        async for chunk in run.stream_text(delta=True):
            yield chunk
