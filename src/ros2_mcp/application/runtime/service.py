"""Application service for read-only ROS runtime operations."""

from ros2_mcp.ros.adapter import RosAdapter


class RuntimeService:
    """Provide ROS runtime use cases independently of ROS implementation details."""

    def __init__(self, ros_adapter: RosAdapter) -> None:
        """Create the service with a ROS adapter implementation."""
        self._ros_adapter = ros_adapter

    def list_nodes(self) -> list[str]:
        """Return currently discovered ROS nodes."""
        return self._ros_adapter.list_nodes()
