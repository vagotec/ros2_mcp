"""MCP server entry point for ROS 2 MCP."""

from mcp.server.mcpserver import MCPServer


def create_server() -> MCPServer:
    """Create and configure the MCP server."""
    return MCPServer(name="ros2-mcp")


def main() -> None:
    """Run the MCP server using the standard stdio transport."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
