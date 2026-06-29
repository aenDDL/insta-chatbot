from unittest.mock import AsyncMock

import pytest
from pydantic_ai import Agent

from app.domain.agent import (
    AgentDependencies,
    AgentOutput,
    AgentService,
    InstagramAction,
    follow_user,
    like_post,
    pass_to_agent,
    send_message,
)
from app.domain.ports import InstagramPort


@pytest.fixture
def mock_instagram() -> InstagramPort:
    return AsyncMock(spec=InstagramPort)


@pytest.fixture
def agent_dependencies(mock_instagram: InstagramPort) -> AgentDependencies:
    return AgentDependencies(mock_instagram)


@pytest.fixture
def agent() -> Agent:
    return Agent(
        "xai:grok-3-mini-fast-latest",
        tools=[send_message, follow_user, like_post],
        output_type=AgentOutput,
    )


@pytest.fixture
def agent_service(agent: Agent, agent_dependencies: AgentDependencies) -> AgentService:
    return AgentService(agent, agent_dependencies)


@pytest.mark.asyncio
async def test_pass_to_agent_follow(
    agent_service: AgentService, mock_instagram: InstagramPort
):
    prompt = "I want to follow user with ID 123."

    result = await pass_to_agent(agent_service, prompt)

    mock_instagram.follow_user.assert_awaited_once_with(123)
    mock_instagram.send_message.assert_not_awaited()
    mock_instagram.like_post.assert_not_awaited()
    assert result.action_taken == InstagramAction.follow_user


@pytest.mark.asyncio
async def test_pass_to_agent_send_message(
    agent_service: AgentService, mock_instagram: InstagramPort
):
    prompt = "Send message 'Hello!' to thread with ID 456."

    result = await pass_to_agent(agent_service, prompt)

    mock_instagram.send_message.assert_awaited_once_with("Hello!", 456)
    mock_instagram.follow_user.assert_not_awaited()
    mock_instagram.like_post.assert_not_awaited()
    assert result.action_taken == InstagramAction.send_message


@pytest.mark.asyncio
async def test_pass_to_agent_like_post(
    agent_service: AgentService, mock_instagram: InstagramPort
):
    prompt = "Like post with ID 789."

    result = await pass_to_agent(agent_service, prompt)

    mock_instagram.like_post.assert_awaited_once_with(789)
    mock_instagram.follow_user.assert_not_awaited()
    mock_instagram.send_message.assert_not_awaited()
    assert result.action_taken == InstagramAction.like_post


@pytest.mark.asyncio
async def test_pass_to_agent_no_action(
    agent_service: AgentService, mock_instagram: InstagramPort
):
    prompt = "What time is it?"

    result = await pass_to_agent(agent_service, prompt)

    mock_instagram.send_message.assert_not_awaited()
    mock_instagram.follow_user.assert_not_awaited()
    mock_instagram.like_post.assert_not_awaited()
    assert result.action_taken is None
