"""Integration tests for the complete MCP server lifespan."""

import asyncio

from mcp import Client

from ros2_mcp.server import create_server


EXPECTED_TOOL_COUNT = 46


async def _verify_server_lifespan() -> None:
    """Enter the real server lifespan and exercise representative tools."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        tools = await client.list_tools()

        names = {
            tool.name
            for tool in tools.tools
        }

        assert len(names) == EXPECTED_TOOL_COUNT

        required_tools = {
            "list_nodes",
            "list_topics",
            "list_actions",
            "read_topic",
            "read_topic_messages",
            "get_runtime_health",
            "get_safety_guardrails",
            "start_ros_process",
        }

        assert required_tools <= names

        safety = await client.call_tool(
            "get_safety_guardrails",
            {},
        )

        assert safety.is_error is False
        assert safety.content

        health = await client.call_tool(
            "get_runtime_health",
            {},
        )

        assert health.is_error is False
        assert health.content

        dry_run = await client.call_tool(
            "start_ros_process",
            {
                "package_name": "demo_nodes_cpp",
                "executable": "talker",
                "dry_run": True,
            },
        )

        assert dry_run.is_error is False
        assert dry_run.content


def test_server_lifespan_initializes_runtime_and_tools() -> None:
    """Verify startup, MCP operations, and clean lifespan shutdown."""
    asyncio.run(
        _verify_server_lifespan()
    )
