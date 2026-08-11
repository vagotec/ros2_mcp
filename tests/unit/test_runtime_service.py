"""Unit tests for the ROS runtime application service."""

from ros2_mcp.application.runtime.service import RuntimeService
from ros2_mcp.ros.adapter import RosAdapter


class FakeRosAdapter(RosAdapter):
    """Provide deterministic ROS data for unit tests."""

    def list_nodes(self) -> list[str]:
        """Return fixed node names."""
        return ["/camera", "/navigation"]


def test_list_nodes_uses_ros_adapter() -> None:
    """Verify that RuntimeService delegates node discovery to the adapter."""
    service = RuntimeService(FakeRosAdapter())

    nodes = service.list_nodes()

    assert nodes == ["/camera", "/navigation"]
