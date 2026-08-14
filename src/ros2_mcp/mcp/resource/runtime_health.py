"""ROS 2 runtime health MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


def register_runtime_health_resource(server: MCPServer) -> None:
    """Register the current ROS 2 runtime health resource."""

    @server.resource(
        "ros2://runtime/health/{scope}",
        name="ROS 2 Runtime Health",
        description="Read the current ROS 2 runtime health summary.",
        mime_type="application/json",
    )
    async def runtime_health(
        scope: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return the current runtime health summary."""
        if scope != "current":
            raise ValueError("Only scope=current is supported.")

        app = ctx.request_context.lifespan_context

        return app.runtime_service.get_runtime_health(
            timeout_sec=app.settings.runtime.read_topic_timeout_sec,
        )
