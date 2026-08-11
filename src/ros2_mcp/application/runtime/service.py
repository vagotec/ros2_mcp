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
