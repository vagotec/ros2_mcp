"""Integration tests for ROS runtime tools through MCP."""

import asyncio

from mcp import Client

from ros2_mcp.server import create_server


async def call_runtime_tools() -> None:
    """Verify that ROS runtime tools are exposed and callable through MCP."""
    server = create_server()

    async with Client(server, raise_exceptions=True) as client:
        tools_result = await client.list_tools()
        tool_names = [tool.name for tool in tools_result.tools]

        assert "list_nodes" in tool_names
        assert "list_topics" in tool_names
        assert "topic_info" in tool_names
        assert "list_services" in tool_names
        assert "read_topic" in tool_names

        nodes_result = await client.call_tool("list_nodes", {})
        topics_result = await client.call_tool("list_topics", {})
        topic_info_result = await client.call_tool(
            "topic_info",
            {"topic_name": "/rosout"},
        )
        services_result = await client.call_tool("list_services", {})
        read_topic_result = await client.call_tool(
            "read_topic",
            {"topic_name": "/rosout"},
        )

        assert nodes_result.is_error is False
        assert topics_result.is_error is False
        assert topic_info_result.is_error is False
        assert services_result.is_error is False
        assert read_topic_result.is_error is False

        assert nodes_result.structured_content is not None
        assert topics_result.structured_content is not None
        assert topic_info_result.structured_content is not None
        assert services_result.structured_content is not None
        assert read_topic_result.structured_content is not None


def test_runtime_tools_through_mcp() -> None:
    """Run the MCP runtime tools integration test."""
    asyncio.run(call_runtime_tools())
