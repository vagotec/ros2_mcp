"""ROS 2 runtime safety MCP resource."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


def register_safety_guardrails_resource(server: MCPServer) -> None:
    """Register the current ros2_mcp safety guardrails resource."""

    @server.resource(
        "ros2://runtime/safety/{scope}",
        name="ROS 2 Runtime Safety",
        description="Read the active ros2_mcp runtime safety guardrails.",
        mime_type="application/json",
    )
    async def safety_guardrails(
        scope: str,
        ctx: Context,
    ) -> dict[str, object]:
        """Return active runtime safety guardrails."""
        if scope != "current":
            raise ValueError("Only scope=current is supported.")

        app = ctx.request_context.lifespan_context

        return app.runtime_service.get_safety_guardrails()
