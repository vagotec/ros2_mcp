"""ROS 2 Jazzy graph runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class GraphMixin:
    """Provide ROS 2 Jazzy graph operations."""

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

    def node_info(self, node_name: str) -> dict[str, object]:
        """Return runtime graph information for a discovered ROS node."""
        base_name, namespace = self._normalize_node_name(node_name)

        if not self._wait_for_node(
            base_name=base_name,
            namespace=namespace,
            timeout_sec=1.0,
        ):
            raise LookupError(f"ROS node not found: {node_name}")

        publishers = self._node.get_publisher_names_and_types_by_node(
            base_name,
            namespace,
        )
        subscribers = self._node.get_subscriber_names_and_types_by_node(
            base_name,
            namespace,
        )
        service_servers = self._node.get_service_names_and_types_by_node(
            base_name,
            namespace,
        )
        service_clients = self._node.get_client_names_and_types_by_node(
            base_name,
            namespace,
        )

        return {
            "node": node_name,
            "publishers": [
                {"name": name, "types": types}
                for name, types in sorted(publishers)
            ],
            "subscribers": [
                {"name": name, "types": types}
                for name, types in sorted(subscribers)
            ],
            "service_servers": [
                {"name": name, "types": types}
                for name, types in sorted(service_servers)
            ],
            "service_clients": [
                {"name": name, "types": types}
                for name, types in sorted(service_clients)
            ],
        }

    def _normalize_node_name(self, node_name: str) -> tuple[str, str]:
        """Split a fully qualified ROS node name into name and namespace."""
        normalized_name = node_name.strip()

        if not normalized_name:
            raise ValueError("Node name must not be empty.")

        normalized_name = normalized_name.lstrip("/")

        if "/" not in normalized_name:
            return normalized_name, "/"

        namespace, base_name = normalized_name.rsplit("/", 1)

        if not base_name:
            raise ValueError(f"Invalid ROS node name: {node_name}")

        return base_name, f"/{namespace}"

    def _wait_for_node(
        self,
        base_name: str,
        namespace: str,
        timeout_sec: float,
    ) -> bool:
        """Wait briefly until a ROS node appears in the local graph."""
        import time

        deadline = time.monotonic() + timeout_sec
        expected = (base_name, namespace)

        while time.monotonic() < deadline:
            if expected in self._node.get_node_names_and_namespaces():
                return True

            remaining = deadline - time.monotonic()

            self._spin_once(
                timeout_sec=min(0.1, max(0.0, remaining))
            )

        return expected in self._node.get_node_names_and_namespaces()
