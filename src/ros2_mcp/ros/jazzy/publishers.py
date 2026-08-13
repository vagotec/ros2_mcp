"""ROS 2 Jazzy publishers runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class PublishersMixin:
    """Provide ROS 2 Jazzy publishers operations."""

    def create_persistent_publisher(
        self,
        topic_name: str,
        message_type: str,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create and register a reusable dynamically typed ROS publisher."""
        # # SAFETY:JazzyRosAdapter:create_persistent_publisher
        self._validate_persistent_publisher_create(topic_name)
        from uuid import uuid4

        normalized_topic = topic_name.strip()
        normalized_type = message_type.strip()

        if not normalized_topic:
            raise ValueError("Topic name must not be empty.")

        if not normalized_topic.startswith("/"):
            normalized_topic = f"/{normalized_topic}"

        if not normalized_type:
            raise ValueError("Message type must not be empty.")

        try:
            ros_message_type = get_message(normalized_type)
        except (
            AttributeError,
            ImportError,
            ModuleNotFoundError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"Unknown ROS message type: {normalized_type}"
            ) from exc

        effective_qos = qos

        if qos and qos.get("auto") is True:
            effective_qos = self._recommend_topic_qos(
                normalized_topic,
                "publisher",
            )

        qos_profile, qos_description = self._build_qos_profile(
            effective_qos
        )

        self._validate_topic_write(normalized_topic)

        publisher = self._node.create_publisher(
            ros_message_type,
            normalized_topic,
            qos_profile,
        )

        publisher_id = uuid4().hex

        self._persistent_publishers[publisher_id] = {
            "publisher": publisher,
            "topic": normalized_topic,
            "type": normalized_type,
            "message_type": ros_message_type,
            "qos": qos_description,
            "publish_count": 0,
        }

        # Allow DDS discovery to begin before returning the publisher.
        self._spin_once(timeout_sec=0.1)

        return {
            "publisher_id": publisher_id,
            "topic": normalized_topic,
            "type": normalized_type,
            "qos": qos_description,
            "subscriber_count": self._node.count_subscribers(
                normalized_topic
            ),
            "publish_count": 0,
            "created": True,
        }

    def publish_with_publisher(
        self,
        publisher_id: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Publish one message through a reusable registered publisher."""
        from rosidl_runtime_py.set_message import set_message_fields

        normalized_id = publisher_id.strip().lower()

        if not normalized_id:
            raise ValueError("publisher_id must not be empty.")

        if not isinstance(message, dict):
            raise TypeError("Message must be a dictionary.")

        entry = self._persistent_publishers.get(normalized_id)

        if entry is None:
            raise LookupError(
                f"Persistent ROS publisher not found: {normalized_id}"
            )

        ros_message = entry["message_type"]()

        try:
            set_message_fields(
                ros_message,
                message,
            )
        except (
            AttributeError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"Invalid message for ROS type "
                f"{entry['type']}: {exc}"
            ) from exc

        publisher = entry["publisher"]

        publisher.publish(ros_message)

        self._spin_once(timeout_sec=0.05)

        entry["publish_count"] += 1

        return {
            "publisher_id": normalized_id,
            "topic": entry["topic"],
            "type": entry["type"],
            "message": message_to_ordereddict(ros_message),
            "qos": entry["qos"],
            "subscriber_count": self._node.count_subscribers(
                entry["topic"]
            ),
            "publish_count": entry["publish_count"],
            "published": True,
        }

    def list_persistent_publishers(
        self,
    ) -> dict[str, object]:
        """Return currently registered reusable ROS publishers."""
        publishers = []

        for publisher_id, entry in sorted(
            self._persistent_publishers.items()
        ):
            publishers.append(
                {
                    "publisher_id": publisher_id,
                    "topic": entry["topic"],
                    "type": entry["type"],
                    "qos": entry["qos"],
                    "subscriber_count": self._node.count_subscribers(
                        entry["topic"]
                    ),
                    "publish_count": entry["publish_count"],
                }
            )

        return {
            "count": len(publishers),
            "publishers": publishers,
        }

    def destroy_persistent_publisher(
        self,
        publisher_id: str,
    ) -> dict[str, object]:
        """Destroy one registered reusable ROS publisher."""
        normalized_id = publisher_id.strip().lower()

        if not normalized_id:
            raise ValueError("publisher_id must not be empty.")

        entry = self._persistent_publishers.get(normalized_id)

        if entry is None:
            raise LookupError(
                f"Persistent ROS publisher not found: {normalized_id}"
            )

        publisher = entry["publisher"]

        self._node.destroy_publisher(publisher)

        del self._persistent_publishers[normalized_id]

        return {
            "publisher_id": normalized_id,
            "topic": entry["topic"],
            "type": entry["type"],
            "publish_count": entry["publish_count"],
            "destroyed": True,
        }
