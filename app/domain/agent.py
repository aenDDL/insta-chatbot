from dataclasses import dataclass, field

from pydantic_ai import Agent, ModelMessage, RunContext

from app.domain.ports import FilesPort, InstagramPort


@dataclass
class AgentDependencies:
    instagram: InstagramPort
    files: FilesPort


@dataclass
class AgentService:
    agent: Agent
    deps: AgentDependencies
    history: list[ModelMessage] = field(default_factory=list, init=False)
    is_authorized: bool = field(default=False, init=False)


async def authorize_on_instagram(deps: AgentDependencies) -> None:
    session = await deps.files.load_instagram_session()
    new_session = await deps.instagram.login(session)
    await deps.files.save_instagram_session(new_session) if new_session else None


async def send_message(
    ctx: RunContext[AgentDependencies], message: str, username: str
) -> None:
    await ctx.deps.instagram.send_message(message, username)


async def follow_user(ctx: RunContext[AgentDependencies], user_id: int) -> None:

    await ctx.deps.instagram.follow_user(user_id)


async def like_post(ctx: RunContext[AgentDependencies], post_id: int) -> None:
    await ctx.deps.instagram.like_post(post_id)


async def stream_agent(service: AgentService, prompt: str):
    if not service.is_authorized:
        await authorize_on_instagram(service.deps)
        service.is_authorized = True
    async with service.agent.run_stream(
        user_prompt=prompt, deps=service.deps, message_history=service.history
    ) as result:
        async for chunk in result.stream_text(delta=True):
            yield chunk
        service.history = result.all_messages()
