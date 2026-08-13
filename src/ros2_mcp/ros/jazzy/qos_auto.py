"""Automatic QoS discovery and recommendation."""

from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    ReliabilityPolicy,
)


class AutoQoSMixin:
    """Inspect DDS endpoints and derive compatible QoS settings."""

    @staticmethod
    def _policy_name(value: object) -> str:
        """Convert a ROS QoS enum to a lowercase name."""
        name = getattr(value, "name", None)

        if name is not None:
            return str(name).lower()

        return str(value)

    def get_topic_qos(
        self,
        topic_name: str,
    ) -> dict[str, object]:
        """Return discovered publisher and subscription QoS profiles."""
        normalized_topic = topic_name.strip()

        if not normalized_topic.startswith("/"):
            normalized_topic = f"/{normalized_topic}"

        publishers = (
            self._node.get_publishers_info_by_topic(
                normalized_topic
            )
        )

        subscriptions = (
            self._node.get_subscriptions_info_by_topic(
                normalized_topic
            )
        )

        def endpoint_data(
            endpoint: object,
        ) -> dict[str, object]:
            profile = endpoint.qos_profile

            return {
                "node_name": endpoint.node_name,
                "node_namespace": endpoint.node_namespace,
                "qos": {
                    "history": self._policy_name(
                        profile.history
                    ),
                    "depth": profile.depth,
                    "reliability": self._policy_name(
                        profile.reliability
                    ),
                    "durability": self._policy_name(
                        profile.durability
                    ),
                },
            }

        return {
            "topic": normalized_topic,
            "publishers": [
                endpoint_data(endpoint)
                for endpoint in publishers
            ],
            "subscriptions": [
                endpoint_data(endpoint)
                for endpoint in subscriptions
            ],
        }

    def _recommend_topic_qos(
        self,
        topic_name: str,
        role: str,
    ) -> dict[str, object]:
        """Derive a compatible QoS profile from discovered endpoints."""
        info = self.get_topic_qos(topic_name)

        if role == "subscription":
            endpoints = info["publishers"]

            if not endpoints:
                return {
                    "history": "keep_last",
                    "depth": 10,
                    "reliability": "reliable",
                    "durability": "volatile",
                }

            reliability = (
                "best_effort"
                if any(
                    item["qos"]["reliability"]
                    == "best_effort"
                    for item in endpoints
                )
                else "reliable"
            )

            durability = (
                "volatile"
                if any(
                    item["qos"]["durability"]
                    == "volatile"
                    for item in endpoints
                )
                else "transient_local"
            )

        elif role == "publisher":
            endpoints = info["subscriptions"]

            if not endpoints:
                return {
                    "history": "keep_last",
                    "depth": 10,
                    "reliability": "reliable",
                    "durability": "volatile",
                }

            reliability = (
                "reliable"
                if any(
                    item["qos"]["reliability"]
                    == "reliable"
                    for item in endpoints
                )
                else "best_effort"
            )

            durability = (
                "transient_local"
                if any(
                    item["qos"]["durability"]
                    == "transient_local"
                    for item in endpoints
                )
                else "volatile"
            )

        else:
            raise ValueError(
                "role must be publisher or subscription."
            )

        depth = max(
            (
                int(item["qos"]["depth"])
                for item in endpoints
                if int(item["qos"]["depth"]) > 0
            ),
            default=10,
        )

        return {
            "history": "keep_last",
            "depth": depth,
            "reliability": reliability,
            "durability": durability,
        }

    def recommend_topic_qos(
        self,
        topic_name: str,
        role: str,
    ) -> dict[str, object]:
        """Return the recommended QoS for a publisher or subscriber."""
        normalized_role = role.strip().lower()

        recommendation = self._recommend_topic_qos(
            topic_name,
            normalized_role,
        )

        return {
            "topic": topic_name,
            "role": normalized_role,
            "recommended_qos": recommendation,
        }
