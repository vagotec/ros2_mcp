"""ROS 2 service inventory MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


def register_services_resource(server: MCPServer) -> None:
    """Register the current ROS 2 service inventory resource."""

    @server.resource(
        "ros2://graph/services/{scope}",
        name="ROS 2 Services",
        description="Read discovered ROS 2 services and their service types.",
        mime_type="application/json",
    )
    async def services(
        scope: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return the current ROS 2 service inventory."""
        if scope != "current":
            raise ValueError("Only scope=current is supported.")

        app = ctx.request_context.lifespan_context

        return {
            "services": app.runtime_service.list_services(),
        }
