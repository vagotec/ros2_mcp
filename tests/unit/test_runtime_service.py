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
        qos: dict[str, object] | None = None,
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
        qos: dict[str, object] | None = None,
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

    def read_rosout(
        self,
        node_name: str | None,
        min_level: str,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return fixed ROS log messages."""
        return {
            "topic": "/rosout",
            "type": "rcl_interfaces/msg/Log",
            "node_filter": node_name,
            "min_level": min_level,
            "max_messages": max_messages,
            "count": 1,
            "messages": [
                {
                    "timestamp": {
                        "sec": 1,
                        "nanosec": 0,
                    },
                    "level": "INFO",
                    "level_value": 20,
                    "node": "camera",
                    "message": "Camera started",
                    "file": "camera.py",
                    "function": "main",
                    "line": 10,
                }
            ],
        }

    def get_diagnostics(
        self,
        name_filter: str | None,
        min_level: int,
        max_messages: int,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return fixed diagnostic status information."""
        return {
            "topic": "/diagnostics",
            "type": "diagnostic_msgs/msg/DiagnosticArray",
            "name_filter": name_filter,
            "min_level": min_level,
            "max_messages": max_messages,
            "count": 1,
            "counts": {
                "OK": 0,
                "WARN": 1,
                "ERROR": 0,
                "STALE": 0,
            },
            "statuses": [
                {
                    "name": "Test Motor",
                    "level": "WARN",
                    "level_value": 1,
                    "message": "Temperature elevated",
                    "hardware_id": "motor-1",
                    "values": {
                        "temperature": "72.5",
                    },
                    "timestamp": {
                        "sec": 1,
                        "nanosec": 0,
                    },
                    "frame_id": "",
                }
            ],
        }

    def get_runtime_health(
        self,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed runtime health summary."""
        return {
            "health": "WARN",
            "graph": {
                "nodes": 3,
                "topics": 7,
                "services": 12,
            },
            "diagnostics": {
                "count": 2,
                "counts": {
                    "OK": 1,
                    "WARN": 1,
                    "ERROR": 0,
                    "STALE": 0,
                },
            },
            "rosout": {
                "count": 1,
                "warn": 1,
                "error": 0,
                "fatal": 0,
            },
        }

    def start_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed managed action goal."""
        return {
            "goal_id": "00112233445566778899aabbccddeeff",
            "action": action_name,
            "type": action_type,
            "goal": goal,
            "accepted": True,
            "status": 2,
            "status_name": "EXECUTING",
            "completed": False,
            "result": None,
            "feedback": [],
        }

    def get_action_status(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return fixed managed action status."""
        return {
            "goal_id": goal_id,
            "status": 2,
            "status_name": "EXECUTING",
            "completed": False,
        }

    def cancel_action_goal(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed successful action cancel result."""
        return {
            "goal_id": goal_id,
            "status": 3,
            "status_name": "CANCELING",
            "completed": False,
            "cancel_requested": True,
            "cancel_accepted": True,
            "cancel_return_code": 0,
            "goals_canceling": 1,
        }

    def list_interfaces(
        self,
        interface_kind: str | None,
        package_name: str | None,
    ) -> dict[str, object]:
        """Return fixed installed interface information."""
        return {
            "interface_kind": interface_kind,
            "package_name": package_name,
            "count": 1,
            "counts": {
                "msg": 1,
                "srv": 0,
                "action": 0,
            },
            "interfaces": [
                {
                    "name": "std_msgs/msg/String",
                    "package": "std_msgs",
                    "kind": "msg",
                    "interface": "String",
                }
            ],
        }

    def interface_info(
        self,
        interface_name: str,
    ) -> dict[str, object]:
        """Return fixed interface field information."""
        return {
            "name": interface_name,
            "package": "std_msgs",
            "kind": "msg",
            "interface": "String",
            "fields": {
                "data": "string",
            },
        }

    def create_persistent_publisher(
        self,
        topic_name: str,
        message_type: str,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Return a fixed reusable publisher."""
        return {
            "publisher_id": "publisher-1",
            "topic": topic_name,
            "type": message_type,
            "qos": qos,
            "subscriber_count": 1,
            "publish_count": 0,
            "created": True,
        }

    def publish_with_publisher(
        self,
        publisher_id: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Return a fixed reusable publisher result."""
        return {
            "publisher_id": publisher_id,
            "message": message,
            "publish_count": 1,
            "published": True,
        }

    def list_persistent_publishers(
        self,
    ) -> dict[str, object]:
        """Return fixed reusable publisher state."""
        return {
            "count": 1,
            "publishers": [
                {
                    "publisher_id": "publisher-1",
                    "topic": "/test",
                    "type": "std_msgs/msg/String",
                    "publish_count": 1,
                }
            ],
        }

    def destroy_persistent_publisher(
        self,
        publisher_id: str,
    ) -> dict[str, object]:
        """Return fixed reusable publisher destruction result."""
        return {
            "publisher_id": publisher_id,
            "destroyed": True,
        }

    def start_ros_process(
        self,
        package_name: str,
        executable: str,
        arguments: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Return a fixed managed ROS process."""
        return {
            "process_id": "process-1",
            "package": package_name,
            "executable": executable,
            "arguments": arguments or [],
            "pid": 1000,
            "running": not dry_run,
            "return_code": None,
            "dry_run": dry_run,
        }

    def get_ros_process(
        self,
        process_id: str,
    ) -> dict[str, object]:
        """Return fixed managed ROS process state."""
        return {
            "process_id": process_id,
            "package": "demo_nodes_cpp",
            "executable": "talker",
            "arguments": [],
            "pid": 1000,
            "running": True,
            "return_code": None,
        }

    def list_ros_processes(
        self,
    ) -> dict[str, object]:
        """Return fixed managed ROS processes."""
        return {
            "count": 1,
            "processes": [
                {
                    "process_id": "process-1",
                    "package": "demo_nodes_cpp",
                    "executable": "talker",
                    "arguments": [],
                    "pid": 1000,
                    "running": True,
                    "return_code": None,
                }
            ],
        }

    def stop_ros_process(
        self,
        process_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed stopped ROS process."""
        return {
            "process_id": process_id,
            "running": False,
            "return_code": 0,
            "stopped": True,
        }

    def start_ros_launch(
        self,
        package_name: str,
        launch_file: str,
        launch_arguments: dict[str, object] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Return a fixed managed ROS launch."""
        return {
            "launch_id": "launch-1",
            "package": package_name,
            "launch_file": launch_file,
            "launch_arguments": launch_arguments or {},
            "pid": 1001,
            "running": not dry_run,
            "return_code": None,
            "dry_run": dry_run,
        }

    def get_ros_launch(
        self,
        launch_id: str,
    ) -> dict[str, object]:
        """Return fixed managed ROS launch state."""
        return {
            "launch_id": launch_id,
            "package": "test_package",
            "launch_file": "test.launch.py",
            "launch_arguments": {},
            "pid": 1001,
            "running": True,
            "return_code": None,
        }

    def list_ros_launches(
        self,
    ) -> dict[str, object]:
        """Return fixed managed ROS launches."""
        return {
            "count": 1,
            "launches": [
                {
                    "launch_id": "launch-1",
                    "package": "test_package",
                    "launch_file": "test.launch.py",
                    "launch_arguments": {},
                    "pid": 1001,
                    "running": True,
                    "return_code": None,
                }
            ],
        }

    def stop_ros_launch(
        self,
        launch_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed stopped ROS launch."""
        return {
            "launch_id": launch_id,
            "running": False,
            "return_code": 0,
            "stopped": True,
        }

    def get_lifecycle_state(
        self,
        node_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed ROS lifecycle state."""
        return {
            "node": node_name,
            "state": {
                "id": 3,
                "label": "active",
            },
        }

    def change_lifecycle_state(
        self,
        node_name: str,
        transition: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed ROS lifecycle transition result."""
        return {
            "node": node_name,
            "transition": transition,
            "transition_id": 3,
            "response": {
                "success": True,
            },
        }

    def start_bag_recording(
        self,
        bag_name: str,
        topics: list[str],
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Return a fixed managed rosbag recording."""
        return {
            "recording_id": "recording-1",
            "bag_path": f"bags/{bag_name}",
            "topics": topics,
            "pid": 1002,
            "running": not dry_run,
            "return_code": None,
            "dry_run": dry_run,
        }

    def stop_bag_recording(
        self,
        recording_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed stopped rosbag recording."""
        return {
            "recording_id": recording_id,
            "running": False,
            "return_code": 0,
            "stopped": True,
        }

    def get_bag_info(
        self,
        bag_name: str,
    ) -> dict[str, object]:
        """Return fixed rosbag information."""
        return {
            "bag_name": bag_name,
            "bag_path": f"bags/{bag_name}",
            "return_code": 0,
            "info": "test bag",
            "error": "",
        }

    def start_bag_playback(
        self,
        bag_name: str,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Return a fixed managed rosbag playback."""
        return {
            "playback_id": "playback-1",
            "bag_path": f"bags/{bag_name}",
            "pid": 1003,
            "running": not dry_run,
            "return_code": None,
            "dry_run": dry_run,
        }

    def stop_bag_playback(
        self,
        playback_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return a fixed stopped rosbag playback."""
        return {
            "playback_id": playback_id,
            "running": False,
            "return_code": 0,
            "stopped": True,
        }

    def get_topic_qos(
        self,
        topic_name: str,
    ) -> dict[str, object]:
        """Return fixed discovered topic QoS."""
        return {
            "topic": topic_name,
            "publishers": [],
            "subscriptions": [],
        }

    def recommend_topic_qos(
        self,
        topic_name: str,
        role: str,
    ) -> dict[str, object]:
        """Return fixed recommended topic QoS."""
        return {
            "topic": topic_name,
            "role": role,
            "recommended_qos": {
                "history": "keep_last",
                "depth": 10,
                "reliability": "reliable",
                "durability": "volatile",
            },
        }

    def get_safety_guardrails(
        self,
    ) -> dict[str, object]:
        """Return fixed runtime safety guardrails."""
        return {
            "arbitrary_shell": False,
            "managed_process_stop_only": True,
            "managed_launch_stop_only": True,
            "managed_rosbag_stop_only": True,
        }


    def list_actions(
        self,
    ) -> list[tuple[str, list[str]]]:
        """Return fixed ROS action discovery data."""
        return [
            (
                "/navigate",
                [
                    "example_interfaces/action/Fibonacci",
                ],
            ),
        ]

    def action_info(
        self,
        action_name: str,
    ) -> dict[str, object]:
        """Return fixed ROS action graph information."""
        return {
            "name": action_name,
            "types": [
                "example_interfaces/action/Fibonacci",
            ],
            "server_count": 1,
            "client_count": 1,
            "servers": [
                "/action_server",
            ],
            "clients": [
                "/action_client",
            ],
            "transport": {
                "send_goal_service": (
                    f"{action_name}/_action/send_goal"
                ),
                "get_result_service": (
                    f"{action_name}/_action/get_result"
                ),
                "cancel_goal_service": (
                    f"{action_name}/_action/cancel_goal"
                ),
                "feedback_topic": (
                    f"{action_name}/_action/feedback"
                ),
                "status_topic": (
                    f"{action_name}/_action/status"
                ),
            },
        }

    def read_topic_messages(
        self,
        topic_name: str,
        max_messages: int,
        duration_sec: float,
        qos: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Return fixed multi-message topic data."""
        messages = [
            {
                "data": f"sample {index}",
            }
            for index in range(
                min(max_messages, 3)
            )
        ]

        return {
            "topic": topic_name,
            "type": "std_msgs/msg/String",
            "count": len(messages),
            "max_messages": max_messages,
            "duration_sec": duration_sec,
            "messages": messages,
            "qos": {
                "history": "keep_last",
                "depth": 10,
                "reliability": "reliable",
                "durability": "volatile",
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

def test_list_actions_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates action discovery."""
    service = RuntimeService(
        FakeRosAdapter()
    )

    assert service.list_actions() == [
        (
            "/navigate",
            [
                "example_interfaces/action/Fibonacci",
            ],
        )
    ]


def test_action_info_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates action inspection."""
    service = RuntimeService(
        FakeRosAdapter()
    )

    result = service.action_info(
        "/navigate"
    )

    assert result["name"] == "/navigate"
    assert result["server_count"] == 1
    assert result["client_count"] == 1


def test_read_topic_messages_uses_ros_adapter() -> None:
    """Verify multi-message topic reading delegation."""
    service = RuntimeService(
        FakeRosAdapter()
    )

    result = service.read_topic_messages(
        topic_name="/samples",
        max_messages=3,
        duration_sec=1.0,
    )

    assert result["count"] == 3
    assert len(result["messages"]) == 3
