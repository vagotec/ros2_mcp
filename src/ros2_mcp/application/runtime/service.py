"""Application service for read-only ROS runtime operations."""

from ros2_mcp.ros.adapter import RosAdapter


class RuntimeService:
    """Provide ROS runtime use cases independently of ROS implementation details."""

    def __init__(self, ros_adapter: RosAdapter) -> None:
        """Create the service with a ROS adapter implementation."""
        self._ros_adapter = ros_adapter

    def list_nodes(self) -> list[str]:
        """Return currently discovered ROS nodes."""
        return self._ros_adapter.list_nodes()

    def list_topics(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS topics with their message types."""
        return self._ros_adapter.list_topics()

    def topic_info(self, topic_name: str) -> dict[str, object]:
        """Return information about a ROS topic."""
        return self._ros_adapter.topic_info(topic_name)

    def list_services(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS services with their service types."""
        return self._ros_adapter.list_services()

    def read_topic(
        self,
        topic_name: str,
        timeout_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read one message from a ROS topic."""
        return self._ros_adapter.read_topic(
            topic_name=topic_name,
            timeout_sec=timeout_sec,
            qos=qos,
        )

    def node_info(self, node_name: str) -> dict[str, object]:
        """Return runtime graph information for a ROS node."""
        return self._ros_adapter.node_info(node_name)

    def list_parameters(self, node_name: str) -> list[str]:
        """Return parameter names exposed by a ROS node."""
        return self._ros_adapter.list_parameters(node_name)

    def get_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> dict[str, object]:
        """Return one parameter value from a ROS node."""
        return self._ros_adapter.get_parameter(
            node_name,
            parameter_name,
        )

    def service_info(self, service_name: str) -> dict[str, object]:
        """Return runtime graph information for a ROS service."""
        return self._ros_adapter.service_info(service_name)


    def publish_topic(
        self,
        topic_name: str,
        message_type: str,
        message: dict[str, object],
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Publish one message to a ROS topic."""
        return self._ros_adapter.publish_topic(
            topic_name=topic_name,
            message_type=message_type,
            message=message,
            qos=qos,
        )

    def call_service(
        self,
        service_name: str,
        service_type: str,
        request: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Call one ROS service and return its response."""
        return self._ros_adapter.call_service(
            service_name=service_name,
            service_type=service_type,
            request=request,
            timeout_sec=timeout_sec,
        )

    def set_parameter(
        self,
        node_name: str,
        parameter_name: str,
        value: object,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Set one parameter on a ROS node."""
        return self._ros_adapter.set_parameter(
            node_name=node_name,
            parameter_name=parameter_name,
            value=value,
            timeout_sec=timeout_sec,
        )

    def send_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Send one ROS action goal and return its result."""
        return self._ros_adapter.send_action_goal(
            action_name=action_name,
            action_type=action_type,
            goal=goal,
            timeout_sec=timeout_sec,
        )

    def read_rosout(
        self,
        node_name: str | None,
        min_level: str,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read structured ROS runtime log messages."""
        return self._ros_adapter.read_rosout(
            node_name=node_name,
            min_level=min_level,
            max_messages=max_messages,
            timeout_sec=timeout_sec,
        )

    def get_diagnostics(
        self,
        name_filter: str | None,
        min_level: int,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read structured ROS diagnostic status information."""
        return self._ros_adapter.get_diagnostics(
            name_filter=name_filter,
            min_level=min_level,
            max_messages=max_messages,
            timeout_sec=timeout_sec,
        )

    def get_runtime_health(
        self,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a compact health summary of the running ROS system."""
        return self._ros_adapter.get_runtime_health(
            timeout_sec=timeout_sec,
        )

    def start_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Start a managed ROS action goal."""
        return self._ros_adapter.start_action_goal(
            action_name=action_name,
            action_type=action_type,
            goal=goal,
            timeout_sec=timeout_sec,
        )

    def get_action_status(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return the state of a managed ROS action goal."""
        return self._ros_adapter.get_action_status(
            goal_id=goal_id,
            timeout_sec=timeout_sec,
        )

    def cancel_action_goal(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Cancel a managed ROS action goal."""
        return self._ros_adapter.cancel_action_goal(
            goal_id=goal_id,
            timeout_sec=timeout_sec,
        )

    def list_interfaces(
        self,
        interface_kind: str | None,
        package_name: str | None,
    ) -> dict[str, object]:
        """List installed ROS interfaces."""

        return self._ros_adapter.list_interfaces(
            interface_kind=interface_kind,
            package_name=package_name,
        )

    def interface_info(
        self,
        interface_name: str,
    ) -> dict[str, object]:
        """Return structured information about one installed ROS interface."""

        return self._ros_adapter.interface_info(
            interface_name=interface_name,
        )

    def create_persistent_publisher(
        self,
        topic_name: str,
        message_type: str,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create a reusable ROS publisher."""
        return self._ros_adapter.create_persistent_publisher(
            topic_name=topic_name,
            message_type=message_type,
            qos=qos,
        )

    def publish_with_publisher(
        self,
        publisher_id: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Publish through a reusable ROS publisher."""
        return self._ros_adapter.publish_with_publisher(
            publisher_id=publisher_id,
            message=message,
        )

    def list_persistent_publishers(
        self,
    ) -> dict[str, object]:
        """List reusable ROS publishers."""
        return self._ros_adapter.list_persistent_publishers()

    def destroy_persistent_publisher(
        self,
        publisher_id: str,
    ) -> dict[str, object]:
        """Destroy one reusable ROS publisher."""
        return self._ros_adapter.destroy_persistent_publisher(
            publisher_id=publisher_id,
        )

    def start_ros_process(
        self,
        package_name: str,
        executable: str,
        arguments: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one controlled ROS executable."""
        return self._ros_adapter.start_ros_process(
            package_name=package_name,
            executable=executable,
            arguments=arguments,
            dry_run=dry_run,
        )

    def get_ros_process(
        self,
        process_id: str,
    ) -> dict[str, object]:
        """Return one managed ROS process."""
        return self._ros_adapter.get_ros_process(
            process_id
        )

    def list_ros_processes(
        self,
    ) -> dict[str, object]:
        """List managed ROS processes."""
        return self._ros_adapter.list_ros_processes()

    def stop_ros_process(
        self,
        process_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one managed ROS process."""
        return self._ros_adapter.stop_ros_process(
            process_id,
            timeout_sec,
        )

    def start_ros_launch(
        self,
        package_name: str,
        launch_file: str,
        launch_arguments: dict[str, object] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one controlled ROS launch file."""
        return self._ros_adapter.start_ros_launch(
            package_name=package_name,
            launch_file=launch_file,
            launch_arguments=launch_arguments,
            dry_run=dry_run,
        )

    def get_ros_launch(
        self,
        launch_id: str,
    ) -> dict[str, object]:
        """Return one managed ROS launch."""
        return self._ros_adapter.get_ros_launch(
            launch_id
        )

    def list_ros_launches(
        self,
    ) -> dict[str, object]:
        """List managed ROS launches."""
        return self._ros_adapter.list_ros_launches()

    def stop_ros_launch(
        self,
        launch_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one managed ROS launch."""
        return self._ros_adapter.stop_ros_launch(
            launch_id,
            timeout_sec,
        )

    def get_lifecycle_state(
        self,
        node_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read one ROS lifecycle state."""
        return self._ros_adapter.get_lifecycle_state(
            node_name,
            timeout_sec,
        )

    def change_lifecycle_state(
        self,
        node_name: str,
        transition: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Change one ROS lifecycle state."""
        return self._ros_adapter.change_lifecycle_state(
            node_name,
            transition,
            timeout_sec,
        )

    def start_bag_recording(
        self,
        bag_name: str,
        topics: list[str],
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start managed rosbag recording."""
        return self._ros_adapter.start_bag_recording(
            bag_name,
            topics,
            dry_run,
        )

    def stop_bag_recording(
        self,
        recording_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop managed rosbag recording."""
        return self._ros_adapter.stop_bag_recording(
            recording_id,
            timeout_sec,
        )

    def get_bag_info(
        self,
        bag_name: str,
    ) -> dict[str, object]:
        """Return rosbag information."""
        return self._ros_adapter.get_bag_info(
            bag_name
        )

    def start_bag_playback(
        self,
        bag_name: str,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start managed rosbag playback."""
        return self._ros_adapter.start_bag_playback(
            bag_name,
            dry_run,
        )

    def stop_bag_playback(
        self,
        playback_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop managed rosbag playback."""
        return self._ros_adapter.stop_bag_playback(
            playback_id,
            timeout_sec,
        )

    def get_topic_qos(
        self,
        topic_name: str,
    ) -> dict[str, object]:
        """Return discovered endpoint QoS."""
        return self._ros_adapter.get_topic_qos(
            topic_name
        )

    def recommend_topic_qos(
        self,
        topic_name: str,
        role: str,
    ) -> dict[str, object]:
        """Return recommended endpoint QoS."""
        return self._ros_adapter.recommend_topic_qos(
            topic_name,
            role,
        )

    def get_safety_guardrails(
        self,
    ) -> dict[str, object]:
        """Return active runtime safety guardrails."""
        return self._ros_adapter.get_safety_guardrails()

    def list_actions(
        self,
    ) -> list[tuple[str, list[str]]]:
        """Return discovered ROS actions."""
        return self._ros_adapter.list_actions()

    def action_info(
        self,
        action_name: str,
    ) -> dict[str, object]:
        """Return runtime graph information for one ROS action."""
        return self._ros_adapter.action_info(
            action_name
        )

    def read_topic_messages(
        self,
        topic_name: str,
        max_messages: int,
        duration_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read multiple messages from one ROS topic."""
        return self._ros_adapter.read_topic_messages(
            topic_name=topic_name,
            max_messages=max_messages,
            duration_sec=duration_sec,
            qos=qos,
        )
