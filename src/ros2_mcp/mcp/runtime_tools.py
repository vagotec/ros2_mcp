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

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_topics(
        ctx: Context["AppContext"],
    ) -> list[tuple[str, list[str]]]:
        """List discovered ROS 2 topics with their message types."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.list_topics()

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def topic_info(
        topic_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return message types and endpoint counts for a ROS 2 topic."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.topic_info(topic_name)

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_services(
        ctx: Context["AppContext"],
    ) -> list[tuple[str, list[str]]]:
        """List discovered ROS 2 services with their service types."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.list_services()

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def read_topic(
        topic_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Read one message from a ROS 2 topic."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.read_topic(
            topic_name=topic_name,
            timeout_sec=app_context.settings.runtime.read_topic_timeout_sec,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def node_info(
        node_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return publishers, subscribers, services, and clients for a ROS node."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.node_info(node_name)

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_parameters(
        node_name: str,
        ctx: Context["AppContext"],
    ) -> list[str]:
        """List parameters exposed by a ROS node."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.list_parameters(node_name)

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def get_parameter(
        node_name: str,
        parameter_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Read one parameter from a ROS node."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.get_parameter(
            node_name,
            parameter_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def service_info(
        service_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return type, servers, and clients for a ROS service."""
        app_context = ctx.request_context.lifespan_context
        return app_context.runtime_service.service_info(service_name)


    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def publish_topic(
        topic_name: str,
        message_type: str,
        message: dict[str, object],
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Publish one message to a ROS 2 topic."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.publish_topic(
            topic_name=topic_name,
            message_type=message_type,
            message=message,
        )
