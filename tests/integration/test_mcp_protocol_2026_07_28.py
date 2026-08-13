"""Integration tests for the MCP 2026-07-28 protocol baseline."""

import asyncio

from mcp import Client

from ros2_mcp.server import create_server


MCP_PROTOCOL_VERSION = "2026-07-28"
EXPECTED_TOOL_COUNT = 46


async def _verify_protocol_baseline() -> None:
    """Verify real MCP operations using the 2026-07-28 protocol."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode=MCP_PROTOCOL_VERSION,
    ) as client:
        assert client.protocol_version == MCP_PROTOCOL_VERSION
        assert client.mode == MCP_PROTOCOL_VERSION

        result = await client.list_tools()

        names = {
            tool.name
            for tool in result.tools
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


async def _verify_tool_schemas() -> None:
    """Verify representative MCP tools expose structured schemas."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode=MCP_PROTOCOL_VERSION,
    ) as client:
        result = await client.list_tools()

        tools = {
            tool.name: tool
            for tool in result.tools
        }

        list_nodes_schema = tools["list_nodes"].input_schema

        assert list_nodes_schema["type"] == "object"
        assert list_nodes_schema["properties"] == {}

        read_topic_schema = tools["read_topic"].input_schema

        assert read_topic_schema["type"] == "object"
        assert "topic_name" in read_topic_schema["properties"]
        assert "topic_name" in read_topic_schema["required"]

        process_schema = tools[
            "start_ros_process"
        ].input_schema

        assert process_schema["type"] == "object"

        properties = process_schema["properties"]

        assert "package_name" in properties
        assert "executable" in properties
        assert "arguments" in properties
        assert "dry_run" in properties

        assert set(process_schema["required"]) == {
            "package_name",
            "executable",
        }

        safety_schema = tools[
            "get_safety_guardrails"
        ].input_schema

        assert safety_schema["type"] == "object"
        assert safety_schema["properties"] == {}


def test_mcp_2026_07_28_protocol_baseline() -> None:
    """Verify real MCP operations on the required protocol baseline."""
    asyncio.run(
        _verify_protocol_baseline()
    )


def test_mcp_2026_07_28_tool_schemas() -> None:
    """Verify representative MCP tool schemas."""
    asyncio.run(
        _verify_tool_schemas()
    )
