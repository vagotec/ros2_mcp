"""ROS 2 Jazzy logging runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class LoggingMixin:
    """Provide ROS 2 Jazzy logging operations."""

    def read_rosout(
        self,
        node_name: str | None,
        min_level: str,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read and filter ROS 2 Jazzy log messages from /rosout."""
        import time

        from rclpy.qos import (
            DurabilityPolicy,
            HistoryPolicy,
            QoSProfile,
            ReliabilityPolicy,
        )
        from rosidl_runtime_py.utilities import get_message

        normalized_level = min_level.strip().upper()

        level_values = {
            "DEBUG": 10,
            "INFO": 20,
            "WARN": 30,
            "WARNING": 30,
            "ERROR": 40,
            "FATAL": 50,
        }

        canonical_levels = {
            10: "DEBUG",
            20: "INFO",
            30: "WARN",
            40: "ERROR",
            50: "FATAL",
        }

        if normalized_level not in level_values:
            raise ValueError(
                "Invalid ROS log level. "
                "Expected DEBUG, INFO, WARN, ERROR, or FATAL."
            )

        if max_messages <= 0:
            raise ValueError("max_messages must be greater than zero.")

        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be greater than zero.")

        normalized_node = None

        if node_name is not None:
            stripped_node = node_name.strip()

            if stripped_node:
                normalized_node = stripped_node.lstrip("/")

        log_type = get_message("rcl_interfaces/msg/Log")

        qos_profile = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1000,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        messages: list[dict[str, object]] = []
        minimum_level_value = level_values[normalized_level]

        def callback(message: object) -> None:
            """Collect matching ROS log messages."""
            if int(message.level) < minimum_level_value:
                return

            if normalized_node is not None:
                logger_name = str(message.name).lstrip("/")

                if logger_name != normalized_node:
                    return

            timestamp = {
                "sec": int(message.stamp.sec),
                "nanosec": int(message.stamp.nanosec),
            }

            messages.append(
                {
                    "timestamp": timestamp,
                    "level": canonical_levels.get(
                        int(message.level),
                        str(int(message.level)),
                    ),
                    "level_value": int(message.level),
                    "node": str(message.name),
                    "message": str(message.msg),
                    "file": str(message.file),
                    "function": str(message.function),
                    "line": int(message.line),
                }
            )

        subscription = self._node.create_subscription(
            log_type,
            "/rosout",
            callback,
            qos_profile,
        )

        deadline = time.monotonic() + timeout_sec

        try:
            while (
                len(messages) < max_messages
                and time.monotonic() < deadline
            ):
                remaining = deadline - time.monotonic()

                if remaining <= 0:
                    break

                self._spin_once(
                    timeout_sec=min(0.1, remaining),
                )
        finally:
            self._node.destroy_subscription(subscription)

        return {
            "topic": "/rosout",
            "type": "rcl_interfaces/msg/Log",
            "node_filter": node_name,
            "min_level": normalized_level,
            "max_messages": max_messages,
            "count": len(messages),
            "messages": messages,
        }
