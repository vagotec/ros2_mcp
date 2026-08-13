"""Abstract ROS adapter interface."""

from abc import ABC, abstractmethod


class RosAdapter(ABC):
    """Define the ROS runtime operations used by the application layer."""

    @abstractmethod
    def list_nodes(self) -> list[str]:
        """Return the names of currently discovered ROS nodes."""
        raise NotImplementedError

    @abstractmethod
    def list_topics(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS topics with their message types."""
        raise NotImplementedError

    @abstractmethod
    def topic_info(self, topic_name: str) -> dict[str, object]:
        """Return information about a ROS topic."""
        raise NotImplementedError

    @abstractmethod
    def list_services(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS services with their types."""
        raise NotImplementedError

    @abstractmethod
    def read_topic(
        self,
        topic_name: str,
        timeout_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read one message from a ROS topic."""
        raise NotImplementedError

    @abstractmethod
    def node_info(self, node_name: str) -> dict[str, object]:
        """Return publishers, subscribers, services, and actions for a node."""
        raise NotImplementedError

    @abstractmethod
    def list_parameters(self, node_name: str) -> list[str]:
        """Return parameter names exposed by a ROS node."""
        raise NotImplementedError

    @abstractmethod
    def get_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> dict[str, object]:
        """Return one parameter value from a ROS node."""
        raise NotImplementedError

    @abstractmethod
    def service_info(self, service_name: str) -> dict[str, object]:
        """Return type, servers, and clients for a ROS service."""
        raise NotImplementedError


    @abstractmethod
    def publish_topic(
        self,
        topic_name: str,
        message_type: str,
        message: dict[str, object],
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Publish one message to a ROS topic."""
        raise NotImplementedError

    @abstractmethod
    def call_service(
        self,
        service_name: str,
        service_type: str,
        request: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Call one ROS service and return its response."""
        raise NotImplementedError

    @abstractmethod
    def set_parameter(
        self,
        node_name: str,
        parameter_name: str,
        value: object,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Set one parameter on a ROS node."""
        raise NotImplementedError

    @abstractmethod
    def send_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Send one ROS action goal and wait for its result."""
        raise NotImplementedError

    @abstractmethod
    def read_rosout(
        self,
        node_name: str | None,
        min_level: str,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read structured ROS log messages from /rosout."""
        raise NotImplementedError

    @abstractmethod
    def get_diagnostics(
        self,
        name_filter: str | None,
        min_level: int,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read structured ROS diagnostic status information."""
        raise NotImplementedError

    @abstractmethod
    def get_runtime_health(
        self,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a compact health summary of the running ROS system."""
        raise NotImplementedError

    @abstractmethod
    def start_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Start a long-running ROS action goal."""
        raise NotImplementedError

    @abstractmethod
    def get_action_status(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return the current state of a managed ROS action goal."""
        raise NotImplementedError

    @abstractmethod
    def cancel_action_goal(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Cancel a managed ROS action goal."""
        raise NotImplementedError

    @abstractmethod
    def list_interfaces(
        self,
        interface_kind: str | None,
        package_name: str | None,
    ) -> dict[str, object]:
        """List installed ROS interfaces."""

        raise NotImplementedError

    @abstractmethod
    def interface_info(
        self,
        interface_name: str,
    ) -> dict[str, object]:
        """Return structured information about one installed ROS interface."""

        raise NotImplementedError

    @abstractmethod
    def create_persistent_publisher(
        self,
        topic_name: str,
        message_type: str,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create a reusable ROS publisher."""
        raise NotImplementedError

    @abstractmethod
    def publish_with_publisher(
        self,
        publisher_id: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Publish a message through a reusable ROS publisher."""
        raise NotImplementedError

    @abstractmethod
    def list_persistent_publishers(
        self,
    ) -> dict[str, object]:
        """List reusable ROS publishers."""
        raise NotImplementedError

    @abstractmethod
    def destroy_persistent_publisher(
        self,
        publisher_id: str,
    ) -> dict[str, object]:
        """Destroy one reusable ROS publisher."""
        raise NotImplementedError

    @abstractmethod
    def start_ros_process(
        self,
        package_name: str,
        executable: str,
        arguments: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one controlled ROS executable."""
        raise NotImplementedError

    @abstractmethod
    def get_ros_process(
        self,
        process_id: str,
    ) -> dict[str, object]:
        """Return one managed ROS process."""
        raise NotImplementedError

    @abstractmethod
    def list_ros_processes(self) -> dict[str, object]:
        """List managed ROS processes."""
        raise NotImplementedError

    @abstractmethod
    def stop_ros_process(
        self,
        process_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one managed ROS process."""
        raise NotImplementedError

    @abstractmethod
    def start_ros_launch(
        self,
        package_name: str,
        launch_file: str,
        launch_arguments: dict[str, object] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one controlled ROS launch."""
        raise NotImplementedError

    @abstractmethod
    def get_ros_launch(
        self,
        launch_id: str,
    ) -> dict[str, object]:
        """Return one managed ROS launch."""
        raise NotImplementedError

    @abstractmethod
    def list_ros_launches(self) -> dict[str, object]:
        """List managed ROS launches."""
        raise NotImplementedError

    @abstractmethod
    def stop_ros_launch(
        self,
        launch_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one managed ROS launch."""
        raise NotImplementedError

    @abstractmethod
    def get_lifecycle_state(
        self,
        node_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return one lifecycle state."""
        raise NotImplementedError

    @abstractmethod
    def change_lifecycle_state(
        self,
        node_name: str,
        transition: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Change one lifecycle state."""
        raise NotImplementedError

    @abstractmethod
    def start_bag_recording(
        self,
        bag_name: str,
        topics: list[str],
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start managed rosbag recording."""
        raise NotImplementedError

    @abstractmethod
    def stop_bag_recording(
        self,
        recording_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop managed rosbag recording."""
        raise NotImplementedError

    @abstractmethod
    def get_bag_info(
        self,
        bag_name: str,
    ) -> dict[str, object]:
        """Return rosbag information."""
        raise NotImplementedError

    @abstractmethod
    def start_bag_playback(
        self,
        bag_name: str,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start managed rosbag playback."""
        raise NotImplementedError

    @abstractmethod
    def stop_bag_playback(
        self,
        playback_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop managed rosbag playback."""
        raise NotImplementedError

    @abstractmethod
    def get_topic_qos(
        self,
        topic_name: str,
    ) -> dict[str, object]:
        """Return discovered topic QoS."""
        raise NotImplementedError

    @abstractmethod
    def recommend_topic_qos(
        self,
        topic_name: str,
        role: str,
    ) -> dict[str, object]:
        """Recommend compatible topic QoS."""
        raise NotImplementedError

    @abstractmethod
    def get_safety_guardrails(
        self,
    ) -> dict[str, object]:
        """Return active runtime safety guardrails."""
        raise NotImplementedError

    @abstractmethod
    def list_actions(
        self,
    ) -> list[tuple[str, list[str]]]:
        """Return discovered ROS actions with their action types."""
        raise NotImplementedError

    @abstractmethod
    def action_info(
        self,
        action_name: str,
    ) -> dict[str, object]:
        """Return runtime graph information for one ROS action."""
        raise NotImplementedError

    @abstractmethod
    def read_topic_messages(
        self,
        topic_name: str,
        max_messages: int,
        duration_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read multiple messages from a ROS topic."""
        raise NotImplementedError
