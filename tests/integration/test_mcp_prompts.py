"""Integration tests for modular ROS 2 MCP prompts."""

import asyncio

from mcp import Client

from ros2_mcp.server import create_server


EXPECTED_TOOL_COUNT = 46

EXPECTED_PROMPTS = {
    "ros_health_check",
    "diagnose_node",
    "diagnose_topic",
    "diagnose_action",
    "inspect_runtime_logs",
    "safe_runtime_review",
}


async def _verify_prompt_inventory() -> None:
    """Verify all Phase 11 prompts are exposed through MCP."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        result = await client.list_prompts()

        names = {
            prompt.name
            for prompt in result.prompts
        }

        assert names == EXPECTED_PROMPTS

        prompt_map = {
            prompt.name: prompt
            for prompt in result.prompts
        }

        assert prompt_map["ros_health_check"].arguments == []
        assert prompt_map["inspect_runtime_logs"].arguments == []
        assert prompt_map["safe_runtime_review"].arguments == []

        assert (
            prompt_map["diagnose_node"].arguments[0].name
            == "node_name"
        )
        assert (
            prompt_map["diagnose_topic"].arguments[0].name
            == "topic_name"
        )
        assert (
            prompt_map["diagnose_action"].arguments[0].name
            == "action_name"
        )

        assert prompt_map["diagnose_node"].arguments[0].required is True
        assert prompt_map["diagnose_topic"].arguments[0].required is True
        assert prompt_map["diagnose_action"].arguments[0].required is True


async def _verify_prompt_rendering() -> None:
    """Verify static and parameterized prompts render correctly."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        health = await client.get_prompt(
            "ros_health_check",
            {},
        )

        assert health.messages
        assert "runtime health check" in (
            health.messages[0].content.text.lower()
        )

        topic = await client.get_prompt(
            "diagnose_topic",
            {
                "topic_name": "/chatter",
            },
        )

        assert topic.messages
        assert "/chatter" in topic.messages[0].content.text
        assert "qos" in topic.messages[0].content.text.lower()

        node = await client.get_prompt(
            "diagnose_node",
            {
                "node_name": "/camera",
            },
        )

        assert "/camera" in node.messages[0].content.text

        action = await client.get_prompt(
            "diagnose_action",
            {
                "action_name": "/navigate_to_pose",
            },
        )

        assert "/navigate_to_pose" in action.messages[0].content.text


async def _verify_prompts_and_tools_coexist() -> None:
    """Verify prompts do not alter the existing MCP tool inventory."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        tools = await client.list_tools()
        prompts = await client.list_prompts()

        assert len(tools.tools) == EXPECTED_TOOL_COUNT
        assert len(prompts.prompts) == len(EXPECTED_PROMPTS)


def test_prompt_inventory() -> None:
    """Verify the Phase 11 MCP prompt inventory."""
    asyncio.run(
        _verify_prompt_inventory()
    )


def test_prompt_rendering() -> None:
    """Verify static and parameterized MCP prompt rendering."""
    asyncio.run(
        _verify_prompt_rendering()
    )


def test_prompts_and_tools_coexist() -> None:
    """Verify MCP Prompts and existing ROS 2 tools coexist."""
    asyncio.run(
        _verify_prompts_and_tools_coexist()
    )
