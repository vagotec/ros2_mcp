"""Unit tests for the ROS runtime application service."""

from ros2_mcp.application.runtime.service import RuntimeService
from ros2_mcp.ros.adapter import RosAdapter


class FakeRosAdapter(RosAdapter):
    """Provide deterministic ROS data for unit tests."""

    def list_nodes(self) -> list[str]:
        """Return fixed node names."""
        return ["/camera", "/navigation"]

    def list_topics(self) -> list[tuple[str, list[str]]]:
        """Return fixed topic names and message types."""
        return [
            ("/camera/image_raw", ["sensor_msgs/msg/Image"]),
            ("/cmd_vel", ["geometry_msgs/msg/Twist"]),
        ]

    def topic_info(self, topic_name: str) -> dict[str, object]:
        """Return fixed information for a topic."""
        return {
            "name": topic_name,
            "types": ["geometry_msgs/msg/Twist"],
            "publisher_count": 1,
            "subscriber_count": 2,
        }

    def list_services(self) -> list[tuple[str, list[str]]]:
        """Return fixed service names and service types."""
        return [
            ("/camera/get_parameters", ["rcl_interfaces/srv/GetParameters"]),
            ("/navigation/change_state", ["lifecycle_msgs/srv/ChangeState"]),
        ]

    def read_topic(
        self,
        topic_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed topic message."""
        return {
            "topic": topic_name,
            "type": "std_msgs/msg/String",
            "message": {
                "data": "hello",
            },
        }


def test_list_nodes_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates node discovery to the adapter."""
    service = RuntimeService(FakeRosAdapter())

    nodes = service.list_nodes()

    assert nodes == ["/camera", "/navigation"]


def test_list_topics_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates topic discovery to the adapter."""
    service = RuntimeService(FakeRosAdapter())

    topics = service.list_topics()

    assert topics == [
        ("/camera/image_raw", ["sensor_msgs/msg/Image"]),
        ("/cmd_vel", ["geometry_msgs/msg/Twist"]),
    ]


def test_topic_info_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates topic inspection to the adapter."""
    service = RuntimeService(FakeRosAdapter())

    info = service.topic_info("/cmd_vel")

    assert info == {
        "name": "/cmd_vel",
        "types": ["geometry_msgs/msg/Twist"],
        "publisher_count": 1,
        "subscriber_count": 2,
    }


def test_list_services_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates service discovery to the adapter."""
    service = RuntimeService(FakeRosAdapter())

    services = service.list_services()

    assert services == [
        ("/camera/get_parameters", ["rcl_interfaces/srv/GetParameters"]),
        ("/navigation/change_state", ["lifecycle_msgs/srv/ChangeState"]),
    ]


def test_read_topic_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates topic reading to the adapter."""
    service = RuntimeService(FakeRosAdapter())

    result = service.read_topic(
        "/chatter",
        timeout_sec=1.0,
    )

    assert result == {
        "topic": "/chatter",
        "type": "std_msgs/msg/String",
        "message": {
            "data": "hello",
        },
    }
