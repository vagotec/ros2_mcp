"""ROS 2 Jazzy adapter implementation."""

from threading import RLock

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message

from ros2_mcp.ros.adapter import RosAdapter
from ros2_mcp.ros.jazzy.actions import ActionsMixin
from ros2_mcp.ros.jazzy.diagnostics import DiagnosticsMixin
from ros2_mcp.ros.jazzy.graph import GraphMixin
from ros2_mcp.ros.jazzy.interfaces import InterfacesMixin
from ros2_mcp.ros.jazzy.logging import LoggingMixin
from ros2_mcp.ros.jazzy.parameters import ParametersMixin
from ros2_mcp.ros.jazzy.publishers import PublishersMixin
from ros2_mcp.ros.jazzy.qos import QoSMixin
from ros2_mcp.ros.jazzy.services import ServicesMixin
from ros2_mcp.ros.jazzy.topics import TopicsMixin
from ros2_mcp.ros.jazzy.launches import LaunchMixin
from ros2_mcp.ros.jazzy.lifecycle import LifecycleMixin
from ros2_mcp.ros.jazzy.processes import ProcessMixin
from ros2_mcp.ros.jazzy.qos_auto import AutoQoSMixin
from ros2_mcp.ros.jazzy.rosbag import RosbagMixin
from ros2_mcp.ros.jazzy.safety import SafetyMixin


class JazzyRosAdapter(
    GraphMixin,
    TopicsMixin,
    ServicesMixin,
    ParametersMixin,
    ActionsMixin,
    LoggingMixin,
    DiagnosticsMixin,
    InterfacesMixin,
    QoSMixin,
    PublishersMixin,
    ProcessMixin,
    LaunchMixin,
    LifecycleMixin,
    RosbagMixin,
    AutoQoSMixin,
    SafetyMixin,
    RosAdapter,
):
    """Provide ROS runtime access through ROS 2 Jazzy and rclpy."""

    _NODE_NAME = "ros2_mcp_runtime"

    def __init__(self) -> None:
        """Initialize an isolated ROS context, node, and executor."""
        self._init_safety()

        self._context = Context()
        rclpy.init(context=self._context)

        self._node = Node(
            self._NODE_NAME,
            context=self._context,
        )

        self._executor = SingleThreadedExecutor(
            context=self._context,
        )
        self._executor.add_node(self._node)

        # Serialize access to the shared rclpy executor across MCP calls.
        self._executor_lock = RLock()

        # Keep long-running action goals available across MCP calls.
        self._active_action_goals: dict[str, dict[str, object]] = {}

        # Keep reusable publishers available across MCP calls.
        self._persistent_publishers: dict[str, dict[str, object]] = {}

        self._init_process_registry()
        self._init_launch_registry()
        self._init_rosbag_registry()

        self._init_process_registry()
        self._init_launch_registry()
        self._init_rosbag_registry()






    def _spin_once(
        self,
        timeout_sec: float,
    ) -> None:
        """Spin the shared executor once under serialization."""
        with self._executor_lock:
            self._executor.spin_once(
                timeout_sec=timeout_sec,
            )

    def _spin_until_future_complete(
        self,
        future: object,
        timeout_sec: float,
    ) -> None:
        """Wait for one ROS future under serialized executor access."""
        with self._executor_lock:
            self._executor.spin_until_future_complete(
                future,
                timeout_sec=timeout_sec,
            )

    def close(self) -> None:
        """Destroy ROS resources owned by this adapter."""
        self._close_rosbags()
        self._close_ros_launches()
        self._close_ros_processes()
        self._close_rosbags()
        self._close_ros_launches()
        self._close_ros_processes()
        for entry in self._active_action_goals.values():
            action_client = entry.get("action_client")

            if action_client is not None:
                destroy = getattr(action_client, "destroy", None)

                if callable(destroy):
                    destroy()

        self._active_action_goals.clear()

        for entry in self._persistent_publishers.values():
            publisher = entry.get("publisher")

            if publisher is not None:
                self._node.destroy_publisher(publisher)

        self._persistent_publishers.clear()

        self._executor.remove_node(self._node)
        self._executor.shutdown()
        self._node.destroy_node()
        rclpy.shutdown(context=self._context)
