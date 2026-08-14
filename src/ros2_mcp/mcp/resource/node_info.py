"""ROS 2 node information MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.resources import ResourceSecurity


def register_node_info_resource(server: MCPServer) -> None:
    """Register the ROS 2 node information resource template."""

    @server.resource(
        "ros2://node/{node_name}",
        name="ROS 2 Node Information",
        description="Read runtime graph information for one ROS 2 node.",
        mime_type="application/json",
        security=ResourceSecurity(
            exempt_params={"node_name"},
        ),
    )
    async def node_info(
        node_name: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return information for one absolute ROS 2 node name."""
        if "\x00" in node_name:
            raise ValueError("ROS node name must not contain a null byte.")

        if not node_name.startswith("/"):
            raise ValueError("ROS node name must be absolute.")

        app = ctx.request_context.lifespan_context

        return app.runtime_service.node_info(node_name)
