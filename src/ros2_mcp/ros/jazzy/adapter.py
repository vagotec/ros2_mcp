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

    def close(self) -> None:
        """Destroy ROS resources owned by this adapter."""
        self._node.destroy_node()
        rclpy.shutdown(context=self._context)
