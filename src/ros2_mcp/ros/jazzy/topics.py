"""ROS 2 Jazzy topics runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class TopicsMixin:
    """Provide ROS 2 Jazzy topics operations."""

    def read_topic(
        self,
        topic_name: str,
        timeout_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read one message from a ROS topic within a timeout."""
        topics = dict(self._node.get_topic_names_and_types())
        topic_types = topics.get(topic_name, [])

        if not topic_types:
            return {
                "topic": topic_name,
                "type": None,
                "message": None,
            }

        message_type_name = topic_types[0]
        message_type = get_message(message_type_name)
        received_message = None

        def callback(message: object) -> None:
            nonlocal received_message
            received_message = message

        effective_qos = qos

        # Reading should adapt to discovered publishers by default.
        # Explicit QoS values still override automatic selection.
        if (
            qos is None
            or qos == {}
            or qos.get("auto") is True
        ):
            effective_qos = self._recommend_topic_qos(
                topic_name,
                "subscription",
            )

        qos_profile, qos_description = self._build_qos_profile(
            effective_qos
        )

        subscription = self._node.create_subscription(
            message_type,
            topic_name,
            callback,
            qos_profile,
        )

        try:
            self._spin_once(
                timeout_sec=timeout_sec,
            )
        finally:
            self._node.destroy_subscription(subscription)

        return {
            "topic": topic_name,
            "type": message_type_name,
            "message": (
                message_to_ordereddict(received_message)
                if received_message is not None
                else None
            ),
            "qos": qos_description,
        }

    def publish_topic(
        self,
        topic_name: str,
        message_type: str,
        message: dict[str, object],
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Publish one dynamically typed message to a ROS topic."""
        # # SAFETY:JazzyRosAdapter:publish_topic
        self._validate_topic_write(topic_name)
        from rosidl_runtime_py.set_message import set_message_fields

        normalized_topic = topic_name.strip()
        normalized_type = message_type.strip()

        if not normalized_topic:
            raise ValueError("Topic name must not be empty.")

        if not normalized_topic.startswith("/"):
            normalized_topic = f"/{normalized_topic}"

        if not normalized_type:
            raise ValueError("Message type must not be empty.")

        if not isinstance(message, dict):
            raise TypeError("Message must be a dictionary.")

        try:
            ros_message_type = get_message(normalized_type)
        except (AttributeError, ImportError, ModuleNotFoundError, ValueError) as exc:
            raise ValueError(
                f"Unknown ROS message type: {normalized_type}"
            ) from exc

        ros_message = ros_message_type()

        try:
            set_message_fields(
                ros_message,
                message,
            )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid message for ROS type {normalized_type}: {exc}"
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

        try:
            # Give DDS a short opportunity to discover existing subscribers.
            self._spin_once(timeout_sec=0.2)

            subscriber_count = self._node.count_subscribers(
                normalized_topic
            )

            publisher.publish(ros_message)

            # Allow the middleware to process the outgoing publication.
            self._spin_once(timeout_sec=0.1)

            return {
                "topic": normalized_topic,
                "type": normalized_type,
                "message": message_to_ordereddict(ros_message),
                "subscriber_count": subscriber_count,
                "published": True,
                "qos": qos_description,
            }
        finally:
            self._node.destroy_publisher(publisher)

    def read_topic_messages(
        self,
        topic_name: str,
        max_messages: int,
        duration_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Read multiple messages from one ROS topic."""
        import time

        normalized_topic = topic_name.strip()

        if not normalized_topic:
            raise ValueError(
                "Topic name must not be empty."
            )

        if not normalized_topic.startswith("/"):
            normalized_topic = (
                f"/{normalized_topic}"
            )

        if (
            not isinstance(max_messages, int)
            or isinstance(max_messages, bool)
            or max_messages <= 0
        ):
            raise ValueError(
                "max_messages must be a positive integer."
            )

        if max_messages > 100:
            raise ValueError(
                "max_messages must not exceed 100."
            )

        if duration_sec <= 0:
            raise ValueError(
                "duration_sec must be greater than zero."
            )

        if duration_sec > 30.0:
            raise ValueError(
                "duration_sec must not exceed 30 seconds."
            )

        topics = dict(
            self._node.get_topic_names_and_types()
        )

        topic_types = topics.get(
            normalized_topic,
            [],
        )

        if not topic_types:
            return {
                "topic": normalized_topic,
                "type": None,
                "count": 0,
                "max_messages": max_messages,
                "duration_sec": duration_sec,
                "messages": [],
                "qos": None,
            }

        message_type_name = topic_types[0]
        message_type = get_message(
            message_type_name
        )

        received_messages: list[
            dict[str, object]
        ] = []

        def callback(message: object) -> None:
            """Collect messages until the configured limit is reached."""
            if (
                len(received_messages)
                >= max_messages
            ):
                return

            received_messages.append(
                message_to_ordereddict(
                    message
                )
            )

        effective_qos = qos

        if (
            qos is None
            or qos == {}
            or qos.get("auto") is True
        ):
            effective_qos = (
                self._recommend_topic_qos(
                    normalized_topic,
                    "subscription",
                )
            )

        (
            qos_profile,
            qos_description,
        ) = self._build_qos_profile(
            effective_qos
        )

        subscription = (
            self._node.create_subscription(
                message_type,
                normalized_topic,
                callback,
                qos_profile,
            )
        )

        deadline = (
            time.monotonic()
            + duration_sec
        )

        try:
            while (
                len(received_messages)
                < max_messages
            ):
                remaining = (
                    deadline
                    - time.monotonic()
                )

                if remaining <= 0:
                    break

                self._spin_once(
                    timeout_sec=min(
                        0.1,
                        remaining,
                    )
                )
        finally:
            self._node.destroy_subscription(
                subscription
            )

        return {
            "topic": normalized_topic,
            "type": message_type_name,
            "count": len(
                received_messages
            ),
            "max_messages": max_messages,
            "duration_sec": duration_sec,
            "messages": received_messages,
            "qos": qos_description,
        }
