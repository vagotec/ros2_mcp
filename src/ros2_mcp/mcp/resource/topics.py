"""ROS 2 topic inventory MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


def register_topics_resource(server: MCPServer) -> None:
    """Register the current ROS 2 topic inventory resource."""

    @server.resource(
        "ros2://graph/topics/{scope}",
        name="ROS 2 Topics",
        description="Read discovered ROS 2 topics and their message types.",
        mime_type="application/json",
    )
    async def topics(
        scope: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return the current ROS 2 topic inventory."""
        if scope != "current":
            raise ValueError("Only scope=current is supported.")

        app = ctx.request_context.lifespan_context

        return {
            "topics": app.runtime_service.list_topics(),
        }
