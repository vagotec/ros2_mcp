"""Integration tests for ROS runtime tools through MCP."""

import asyncio

from mcp import Client

from ros2_mcp.server import create_server


async def call_list_nodes() -> None:
    """Verify that list_nodes is exposed and callable through MCP."""
    server = create_server()

    async with Client(server, raise_exceptions=True) as client:
        tools_result = await client.list_tools()
        tool_names = [tool.name for tool in tools_result.tools]

        assert "list_nodes" in tool_names

        result = await client.call_tool("list_nodes", {})

        assert result.is_error is False
        assert result.structured_content is not None


def test_list_nodes_through_mcp() -> None:
    """Run the MCP runtime tool integration test."""
    asyncio.run(call_list_nodes())
