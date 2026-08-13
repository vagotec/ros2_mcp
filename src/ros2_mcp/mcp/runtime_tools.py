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
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read one message from a ROS 2 topic."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.read_topic(
            topic_name=topic_name,
            timeout_sec=app_context.settings.runtime.read_topic_timeout_sec,
            qos=qos,
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
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Publish one message to a ROS 2 topic."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.publish_topic(
            topic_name=topic_name,
            message_type=message_type,
            message=message,
            qos=qos,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def call_service(
        service_name: str,
        service_type: str,
        request: dict[str, object],
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Call one ROS 2 service."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.call_service(
            service_name=service_name,
            service_type=service_type,
            request=request,
            timeout_sec=1.0,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def set_parameter(
        node_name: str,
        parameter_name: str,
        value: object,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Set one parameter on a ROS 2 node."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.set_parameter(
            node_name=node_name,
            parameter_name=parameter_name,
            value=value,
            timeout_sec=1.0,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def send_action_goal(
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Send one ROS 2 action goal and wait for its result."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.send_action_goal(
            action_name=action_name,
            action_type=action_type,
            goal=goal,
            timeout_sec=5.0,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def read_rosout(
        ctx: Context["AppContext"],
        node_name: str | None = None,
        min_level: str = "INFO",
        max_messages: int = 50,
    ) -> dict[str, object]:
        """Read filtered ROS 2 runtime log messages from /rosout."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.read_rosout(
            node_name=node_name,
            min_level=min_level,
            max_messages=max_messages,
            timeout_sec=app_context.settings.runtime.read_topic_timeout_sec,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def get_diagnostics(
        ctx: Context["AppContext"],
        name_filter: str | None = None,
        min_level: int = 0,
        max_messages: int = 50,
    ) -> dict[str, object]:
        """Read filtered ROS 2 diagnostic status information."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.get_diagnostics(
            name_filter=name_filter,
            min_level=min_level,
            max_messages=max_messages,
            timeout_sec=app_context.settings.runtime.read_topic_timeout_sec,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def get_runtime_health(
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return a compact ROS 2 runtime health summary."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.get_runtime_health(
            timeout_sec=app_context.settings.runtime.read_topic_timeout_sec,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def start_action_goal(
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Start a managed ROS 2 action goal."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.start_action_goal(
            action_name=action_name,
            action_type=action_type,
            goal=goal,
            timeout_sec=5.0,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def get_action_status(
        goal_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return the state of a managed ROS 2 action goal."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.get_action_status(
            goal_id=goal_id,
            timeout_sec=0.2,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def cancel_action_goal(
        goal_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Cancel a managed ROS 2 action goal."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.cancel_action_goal(
            goal_id=goal_id,
            timeout_sec=5.0,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_interfaces(
        ctx: Context["AppContext"],
        interface_kind: str | None = None,
        package_name: str | None = None,
    ) -> dict[str, object]:
        """List installed ROS 2 message, service, and action interfaces."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.list_interfaces(
            interface_kind=interface_kind,
            package_name=package_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def interface_info(
        interface_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Describe one installed ROS 2 interface."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.interface_info(
            interface_name=interface_name,
        )


    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def create_persistent_publisher(
        topic_name: str,
        message_type: str,
        ctx: Context["AppContext"],
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create a reusable ROS 2 publisher."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.create_persistent_publisher(
            topic_name=topic_name,
            message_type=message_type,
            qos=qos,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def publish_with_publisher(
        publisher_id: str,
        message: dict[str, object],
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Publish through a reusable ROS 2 publisher."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.publish_with_publisher(
            publisher_id=publisher_id,
            message=message,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_persistent_publishers(
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """List reusable ROS 2 publishers."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.list_persistent_publishers()

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=True,
            idempotent_hint=False,
            open_world_hint=False,
        )
    )
    def destroy_persistent_publisher(
        publisher_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Destroy one reusable ROS 2 publisher."""
        app_context = ctx.request_context.lifespan_context

        return app_context.runtime_service.destroy_persistent_publisher(
            publisher_id=publisher_id,
        )

    @server.tool()
    def start_ros_process(
        package_name: str,
        executable: str,
        ctx: Context["AppContext"],
        arguments: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one controlled ROS executable."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.start_ros_process(
            package_name,
            executable,
            arguments,
            dry_run,
        )

    @server.tool()
    def get_ros_process(
        process_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return one managed ROS process."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.get_ros_process(
            process_id
        )

    @server.tool()
    def list_ros_processes(
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """List managed ROS processes."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.list_ros_processes()

    @server.tool()
    def stop_ros_process(
        process_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Stop one managed ROS process."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.stop_ros_process(
            process_id,
            5.0,
        )

    @server.tool()
    def start_ros_launch(
        package_name: str,
        launch_file: str,
        ctx: Context["AppContext"],
        launch_arguments: dict[str, object] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one controlled ROS launch file."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.start_ros_launch(
            package_name,
            launch_file,
            launch_arguments,
            dry_run,
        )

    @server.tool()
    def get_ros_launch(
        launch_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return one managed ROS launch."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.get_ros_launch(
            launch_id
        )

    @server.tool()
    def list_ros_launches(
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """List managed ROS launches."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.list_ros_launches()

    @server.tool()
    def stop_ros_launch(
        launch_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Stop one managed ROS launch."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.stop_ros_launch(
            launch_id,
            5.0,
        )

    @server.tool()
    def get_lifecycle_state(
        node_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return one ROS lifecycle state."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.get_lifecycle_state(
            node_name,
            3.0,
        )

    @server.tool()
    def change_lifecycle_state(
        node_name: str,
        transition: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Request one ROS lifecycle transition."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.change_lifecycle_state(
            node_name,
            transition,
            3.0,
        )

    @server.tool()
    def start_bag_recording(
        bag_name: str,
        topics: list[str],
        ctx: Context["AppContext"],
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start managed rosbag recording."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.start_bag_recording(
            bag_name,
            topics,
            dry_run,
        )

    @server.tool()
    def stop_bag_recording(
        recording_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Stop managed rosbag recording."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.stop_bag_recording(
            recording_id,
            5.0,
        )

    @server.tool()
    def get_bag_info(
        bag_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return information about a managed rosbag."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.get_bag_info(
            bag_name
        )

    @server.tool()
    def start_bag_playback(
        bag_name: str,
        ctx: Context["AppContext"],
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start managed rosbag playback."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.start_bag_playback(
            bag_name,
            dry_run,
        )

    @server.tool()
    def stop_bag_playback(
        playback_id: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Stop managed rosbag playback."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.stop_bag_playback(
            playback_id,
            5.0,
        )

    @server.tool()
    def get_topic_qos(
        topic_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Inspect endpoint QoS for one ROS topic."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.get_topic_qos(
            topic_name
        )

    @server.tool()
    def recommend_topic_qos(
        topic_name: str,
        role: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Recommend compatible QoS for a publisher or subscription."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.recommend_topic_qos(
            topic_name,
            role,
        )

    @server.tool()
    def get_safety_guardrails(
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return active generic ROS runtime safety guardrails."""
        app = ctx.request_context.lifespan_context
        return app.runtime_service.get_safety_guardrails()

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def list_actions(
        ctx: Context["AppContext"],
    ) -> list[tuple[str, list[str]]]:
        """List discovered ROS 2 actions and their action types."""
        app_context = (
            ctx.request_context.lifespan_context
        )

        return (
            app_context.runtime_service
            .list_actions()
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def action_info(
        action_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, object]:
        """Return servers, clients, types, and endpoints for one ROS action."""
        app_context = (
            ctx.request_context.lifespan_context
        )

        return (
            app_context.runtime_service
            .action_info(
                action_name
            )
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        )
    )
    def read_topic_messages(
        topic_name: str,
        ctx: Context["AppContext"],
        max_messages: int = 10,
        duration_sec: float = 1.0,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read multiple ROS 2 topic messages using automatic QoS by default."""
        app_context = (
            ctx.request_context.lifespan_context
        )

        return (
            app_context.runtime_service
            .read_topic_messages(
                topic_name=topic_name,
                max_messages=max_messages,
                duration_sec=duration_sec,
                qos=qos,
            )
        )
