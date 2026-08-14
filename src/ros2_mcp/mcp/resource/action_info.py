"""ROS 2 action information MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.resources import ResourceSecurity


def register_action_info_resource(server: MCPServer) -> None:
    """Register the ROS 2 action information resource template."""

    @server.resource(
        "ros2://action/{action_name}",
        name="ROS 2 Action Information",
        description="Read runtime graph information for one ROS 2 action.",
        mime_type="application/json",
        security=ResourceSecurity(
            exempt_params={"action_name"},
        ),
    )
    async def action_info(
        action_name: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return information for one absolute ROS 2 action name."""
        if "\x00" in action_name:
            raise ValueError("ROS action name must not contain a null byte.")

        if not action_name.startswith("/"):
            raise ValueError("ROS action name must be absolute.")

        app = ctx.request_context.lifespan_context

        return app.runtime_service.action_info(action_name)
