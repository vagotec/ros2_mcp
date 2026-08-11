"""Unit tests for the MCP server entry point."""

from mcp.server.mcpserver import MCPServer

from ros2_mcp.server import create_server


def test_create_server_returns_mcp_server() -> None:
    """Verify that the server factory creates an MCPServer instance."""
    server = create_server()

    assert isinstance(server, MCPServer)
