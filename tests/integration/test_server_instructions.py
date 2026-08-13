"""Integration tests for ros2_mcp server instructions."""

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ros2_mcp.mcp.instructions import SERVER_INSTRUCTIONS
from ros2_mcp.server import create_server


EXPECTED_TOOL_COUNT = 46


def test_server_exposes_instructions() -> None:
    """Verify the MCP server is configured with project instructions."""
    server = create_server()

    assert server.instructions == SERVER_INSTRUCTIONS
    assert "controlled MCP interface" in server.instructions
    assert "Prefer read-only inspection" in server.instructions
    assert "dry_run=true" in server.instructions
    assert "safety guardrails" in server.instructions


async def _verify_stdio_instructions() -> None:
    """Verify instructions are delivered through the real stdio transport."""
    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "ros2_mcp.server",
        ],
        env=dict(os.environ),
    )

    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as session:
            result = await session.initialize()

            assert result.instructions == SERVER_INSTRUCTIONS

            tools = await session.list_tools()

            assert len(tools.tools) == EXPECTED_TOOL_COUNT


def test_stdio_delivers_server_instructions() -> None:
    """Verify a stdio MCP client receives the server instructions."""
    asyncio.run(
        _verify_stdio_instructions()
    )
