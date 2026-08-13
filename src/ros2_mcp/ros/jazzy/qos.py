"""ROS 2 Jazzy qos runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class QoSMixin:
    """Provide ROS 2 Jazzy qos operations."""

    @staticmethod
    def _build_qos_profile(
        qos: dict[str, object] | None,
    ) -> tuple[object, dict[str, object]]:
        """Build and validate a ROS 2 QoS profile."""
        from rclpy.qos import (
            DurabilityPolicy,
            HistoryPolicy,
            QoSProfile,
            ReliabilityPolicy,
        )

        values = dict(qos or {})

        history_name = str(
            values.get("history", "keep_last")
        ).strip().lower()

        reliability_name = str(
            values.get("reliability", "reliable")
        ).strip().lower()

        durability_name = str(
            values.get("durability", "volatile")
        ).strip().lower()

        raw_depth = values.get("depth", 10)

        if isinstance(raw_depth, bool):
            raise ValueError(
                "QoS depth must be a positive integer."
            )

        try:
            depth = int(raw_depth)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "QoS depth must be a positive integer."
            ) from exc

        if depth <= 0:
            raise ValueError(
                "QoS depth must be a positive integer."
            )

        histories = {
            "keep_last": HistoryPolicy.KEEP_LAST,
            "keep_all": HistoryPolicy.KEEP_ALL,
        }

        reliabilities = {
            "reliable": ReliabilityPolicy.RELIABLE,
            "best_effort": ReliabilityPolicy.BEST_EFFORT,
        }

        durabilities = {
            "volatile": DurabilityPolicy.VOLATILE,
            "transient_local": DurabilityPolicy.TRANSIENT_LOCAL,
        }

        if history_name not in histories:
            raise ValueError(
                "QoS history must be keep_last or keep_all."
            )

        if reliability_name not in reliabilities:
            raise ValueError(
                "QoS reliability must be reliable or best_effort."
            )

        if durability_name not in durabilities:
            raise ValueError(
                "QoS durability must be volatile or transient_local."
            )

        profile = QoSProfile(
            history=histories[history_name],
            depth=depth,
            reliability=reliabilities[reliability_name],
            durability=durabilities[durability_name],
        )

        description = {
            "history": history_name,
            "depth": depth,
            "reliability": reliability_name,
            "durability": durability_name,
        }

        return profile, description
