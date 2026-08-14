"""ROS 2 action inventory MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


def register_actions_resource(server: MCPServer) -> None:
    """Register the current ROS 2 action inventory resource."""

    @server.resource(
        "ros2://graph/actions/{scope}",
        name="ROS 2 Actions",
        description="Read discovered ROS 2 actions and their action types.",
        mime_type="application/json",
    )
    async def actions(
        scope: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return the current ROS 2 action inventory."""
        if scope != "current":
            raise ValueError("Only scope=current is supported.")

        app = ctx.request_context.lifespan_context

        return {
            "actions": app.runtime_service.list_actions(),
        }
