"""MCP tools for read-only ROS runtime operations."""

from typing import TYPE_CHECKING

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.types import ToolAnnotations

if TYPE_CHECKING:
    from ros2_mcp.server import AppContext


def register_runtime_tools(server: MCPServer) -> None:
    """Register read-only ROS runtime tools with the MCP server."""

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_nodes(ctx: Context["AppContext"]) -> list[str]:
        """List currently discovered ROS 2 nodes."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.list_nodes()
