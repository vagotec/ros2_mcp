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
    ) -> dict[str, object]:
        """Read one message from a ROS topic."""
        return self._ros_adapter.read_topic(topic_name, timeout_sec)

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
    ) -> dict[str, object]:
        """Publish one message to a ROS topic."""
        return self._ros_adapter.publish_topic(
            topic_name=topic_name,
            message_type=message_type,
            message=message,
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
