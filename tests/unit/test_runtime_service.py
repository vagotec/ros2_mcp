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
            (
                "/camera/get_parameters",
                ["rcl_interfaces/srv/GetParameters"],
            ),
            (
                "/navigation/change_state",
                ["lifecycle_msgs/srv/ChangeState"],
            ),
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

    def node_info(self, node_name: str) -> dict[str, object]:
        """Return fixed node graph information."""
        return {
            "node": node_name,
            "publishers": [],
            "subscribers": [],
            "service_servers": [],
            "service_clients": [],
        }

    def list_parameters(self, node_name: str) -> list[str]:
        """Return fixed parameter names."""
        return [
            "start_type_description_service",
            "use_sim_time",
        ]

    def get_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> dict[str, object]:
        """Return a fixed parameter value."""
        return {
            "node": node_name,
            "parameter": parameter_name,
            "type": "bool",
            "value": False,
        }

    def service_info(self, service_name: str) -> dict[str, object]:
        """Return fixed service graph information."""
        return {
            "service": service_name,
            "types": ["rcl_interfaces/srv/GetParameters"],
            "servers": ["/camera"],
            "clients": [],
        }

    def publish_topic(
        self,
        topic_name: str,
        message_type: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Return a fixed publication result."""
        return {
            "topic": topic_name,
            "type": message_type,
            "message": message,
            "subscriber_count": 1,
            "published": True,
        }

    def call_service(
        self,
        service_name: str,
        service_type: str,
        request: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed service-call result."""
        return {
            "service": service_name,
            "type": service_type,
            "request": request,
            "response": {
                "success": True,
                "message": "ok",
            },
            "completed": True,
        }

    def set_parameter(
        self,
        node_name: str,
        parameter_name: str,
        value: object,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed parameter update result."""
        return {
            "node": node_name,
            "parameter": parameter_name,
            "value": value,
            "successful": True,
            "reason": "",
        }

    def send_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed action result."""
        return {
            "action": action_name,
            "type": action_type,
            "goal": goal,
            "accepted": True,
            "status": 4,
            "result": {
                "sequence": [0, 1, 1, 2, 3],
            },
            "feedback": [],
            "completed": True,
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
        (
            "/camera/get_parameters",
            ["rcl_interfaces/srv/GetParameters"],
        ),
        (
            "/navigation/change_state",
            ["lifecycle_msgs/srv/ChangeState"],
        ),
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
