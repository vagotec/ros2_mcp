"""ROS 2 Jazzy adapter implementation."""

import rclpy
from rclpy.context import Context
from rclpy.node import Node

from ros2_mcp.ros.adapter import RosAdapter


class JazzyRosAdapter(RosAdapter):
    """Provide ROS runtime access through ROS 2 Jazzy and rclpy."""

    _NODE_NAME = "ros2_mcp_runtime"

    def __init__(self) -> None:
        """Initialize an isolated ROS context and internal discovery node."""
        self._context = Context()
        rclpy.init(context=self._context)

        self._node = Node(
            self._NODE_NAME,
            context=self._context,
        )

    def list_nodes(self) -> list[str]:
        """Return discovered ROS nodes excluding the internal MCP node."""
        nodes = self._node.get_node_names()

        return sorted(
            node_name
            for node_name in nodes
            if node_name != self._NODE_NAME
        )

    def list_topics(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS topics with their message types."""
        topics = self._node.get_topic_names_and_types()

        return sorted(
            (topic_name, sorted(topic_types))
            for topic_name, topic_types in topics
        )

    def topic_info(self, topic_name: str) -> dict[str, object]:
        """Return types and endpoint counts for a ROS topic."""
        topics = dict(self._node.get_topic_names_and_types())

        return {
            "name": topic_name,
            "types": sorted(topics.get(topic_name, [])),
            "publisher_count": self._node.count_publishers(topic_name),
            "subscriber_count": self._node.count_subscribers(topic_name),
        }

    def list_services(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS services excluding internal MCP services."""
        services = self._node.get_service_names_and_types()
        internal_prefix = f"/{self._NODE_NAME}/"

        return sorted(
            (service_name, sorted(service_types))
            for service_name, service_types in services
            if not service_name.startswith(internal_prefix)
        )

    def close(self) -> None:
        """Destroy ROS resources owned by this adapter."""
        self._node.destroy_node()
        rclpy.shutdown(context=self._context)
