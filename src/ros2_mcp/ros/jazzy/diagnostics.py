"""ROS 2 Jazzy diagnostics runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class DiagnosticsMixin:
    """Provide ROS 2 Jazzy diagnostics operations."""

    def get_diagnostics(
        self,
        name_filter: str | None,
        min_level: int,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read and filter diagnostic status entries from /diagnostics."""
        import time

        from diagnostic_msgs.msg import DiagnosticArray
        from rclpy.qos import (
            DurabilityPolicy,
            HistoryPolicy,
            QoSProfile,
            ReliabilityPolicy,
        )

        level_names = {
            0: "OK",
            1: "WARN",
            2: "ERROR",
            3: "STALE",
        }

        if min_level not in level_names:
            raise ValueError(
                "min_level must be one of 0 (OK), 1 (WARN), "
                "2 (ERROR), or 3 (STALE)."
            )

        if max_messages <= 0:
            raise ValueError("max_messages must be greater than zero.")

        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be greater than zero.")

        normalized_filter = None

        if name_filter is not None:
            stripped_filter = name_filter.strip()

            if stripped_filter:
                normalized_filter = stripped_filter.casefold()

        statuses: list[dict[str, object]] = []

        qos_profile = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )

        def callback(message: DiagnosticArray) -> None:
            """Collect matching diagnostic status entries."""
            for status in message.status:
                if len(statuses) >= max_messages:
                    return

                raw_level = status.level

                if isinstance(raw_level, bytes):
                    if len(raw_level) != 1:
                        raise ValueError(
                            "DiagnosticStatus.level must contain exactly one byte."
                        )

                    status_level = raw_level[0]
                else:
                    status_level = int(raw_level)

                if status_level < min_level:
                    continue

                if (
                    normalized_filter is not None
                    and normalized_filter not in status.name.casefold()
                ):
                    continue

                statuses.append(
                    {
                        "name": str(status.name),
                        "level": level_names.get(
                            status_level,
                            str(status_level),
                        ),
                        "level_value": status_level,
                        "message": str(status.message),
                        "hardware_id": str(status.hardware_id),
                        "values": {
                            str(value.key): str(value.value)
                            for value in status.values
                        },
                        "timestamp": {
                            "sec": int(message.header.stamp.sec),
                            "nanosec": int(message.header.stamp.nanosec),
                        },
                        "frame_id": str(message.header.frame_id),
                    }
                )

        subscription = self._node.create_subscription(
            DiagnosticArray,
            "/diagnostics",
            callback,
            qos_profile,
        )

        deadline = time.monotonic() + timeout_sec

        try:
            while (
                len(statuses) < max_messages
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

        counts = {
            "OK": 0,
            "WARN": 0,
            "ERROR": 0,
            "STALE": 0,
        }

        for status in statuses:
            level = status["level"]

            if level in counts:
                counts[level] += 1

        return {
            "topic": "/diagnostics",
            "type": "diagnostic_msgs/msg/DiagnosticArray",
            "name_filter": name_filter,
            "min_level": min_level,
            "max_messages": max_messages,
            "count": len(statuses),
            "counts": counts,
            "statuses": statuses,
        }

    def get_runtime_health(
        self,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Aggregate ROS graph, diagnostics, and recent log health."""
        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be greater than zero.")

        nodes = self._node.get_node_names_and_namespaces()
        topics = self._node.get_topic_names_and_types()
        services = self._node.get_service_names_and_types()

        diagnostics = self.get_diagnostics(
            name_filter=None,
            min_level=0,
            max_messages=50,
            timeout_sec=timeout_sec,
        )

        rosout = self.read_rosout(
            node_name=None,
            min_level="WARN",
            max_messages=50,
            timeout_sec=timeout_sec,
        )

        diagnostic_counts = diagnostics["counts"]

        warn_count = int(diagnostic_counts.get("WARN", 0))
        error_count = int(diagnostic_counts.get("ERROR", 0))
        stale_count = int(diagnostic_counts.get("STALE", 0))

        log_warn_count = 0
        log_error_count = 0
        log_fatal_count = 0

        for message in rosout["messages"]:
            level = message.get("level")

            if level == "WARN":
                log_warn_count += 1
            elif level == "ERROR":
                log_error_count += 1
            elif level == "FATAL":
                log_fatal_count += 1

        if error_count > 0 or log_error_count > 0 or log_fatal_count > 0:
            health = "ERROR"
        elif warn_count > 0 or stale_count > 0 or log_warn_count > 0:
            health = "WARN"
        else:
            health = "OK"

        return {
            "health": health,
            "graph": {
                "nodes": len(nodes),
                "topics": len(topics),
                "services": len(services),
            },
            "diagnostics": {
                "count": diagnostics["count"],
                "counts": diagnostic_counts,
            },
            "rosout": {
                "count": rosout["count"],
                "warn": log_warn_count,
                "error": log_error_count,
                "fatal": log_fatal_count,
            },
        }
