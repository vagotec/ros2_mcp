"""ROS 2 topic information MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.resources import ResourceSecurity


def register_topic_info_resource(server: MCPServer) -> None:
    """Register the ROS 2 topic information resource template."""

    @server.resource(
        "ros2://topic/{topic_name}",
        name="ROS 2 Topic Information",
        description="Read runtime information for one ROS 2 topic.",
        mime_type="application/json",
        security=ResourceSecurity(
            exempt_params={"topic_name"},
        ),
    )
    async def topic_info(
        topic_name: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return information for one absolute ROS 2 topic name."""
        if "\x00" in topic_name:
            raise ValueError("ROS topic name must not contain a null byte.")

        if not topic_name.startswith("/"):
            raise ValueError("ROS topic name must be absolute.")

        app = ctx.request_context.lifespan_context

        return app.runtime_service.topic_info(topic_name)
