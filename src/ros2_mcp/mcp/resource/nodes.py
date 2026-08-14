"""ROS 2 node inventory MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


def register_nodes_resource(server: MCPServer) -> None:
    """Register the current ROS 2 node inventory resource."""

    @server.resource(
        "ros2://graph/nodes/{scope}",
        name="ROS 2 Nodes",
        description="Read the currently discovered ROS 2 nodes.",
        mime_type="application/json",
    )
    async def nodes(
        scope: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return the current ROS 2 node inventory."""
        if scope != "current":
            raise ValueError("Only scope=current is supported.")

        app = ctx.request_context.lifespan_context

        return {
            "nodes": app.runtime_service.list_nodes(),
        }
