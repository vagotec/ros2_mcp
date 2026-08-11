"""Application service for ROS 2 project operations."""

from ros2_mcp.project.adapter import ProjectAdapter


class ProjectService:
    """Provide project use cases independently of filesystem implementation."""

    def __init__(self, project_adapter: ProjectAdapter) -> None:
        """Create the service with a project adapter implementation."""
        self._project_adapter = project_adapter

    def create_workspace(self, workspace_path: str) -> dict[str, str]:
        """Create a ROS 2 workspace inside the allowed project root."""
        return self._project_adapter.create_workspace(workspace_path)

    def create_package(
        self,
        workspace_path: str,
        package_name: str,
    ) -> dict[str, str]:
        """Create a ROS 2 Python package inside a workspace."""
        return self._project_adapter.create_package(
            workspace_path,
            package_name,
        )

    def create_node(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
    ) -> dict[str, str]:
        """Create a Python ROS 2 node inside an existing package."""
        return self._project_adapter.create_node(
            workspace_path,
            package_name,
            node_name,
        )

    def create_launch_file(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
        launch_name: str,
    ) -> dict[str, str]:
        """Create a Python launch file for an existing ROS 2 package."""
        return self._project_adapter.create_launch_file(
            workspace_path,
            package_name,
            node_name,
            launch_name,
        )

    def create_parameter_file(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
        parameter_file_name: str,
    ) -> dict[str, str]:
        """Create a ROS 2 parameter YAML file for an existing package."""
        return self._project_adapter.create_parameter_file(
            workspace_path,
            package_name,
            node_name,
            parameter_file_name,
        )

    def create_tests(
        self,
        workspace_path: str,
        package_name: str,
    ) -> dict[str, str]:
        """Create basic tests for an existing ROS 2 package."""
        return self._project_adapter.create_tests(
            workspace_path,
            package_name,
        )
