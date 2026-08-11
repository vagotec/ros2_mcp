"""Abstract project adapter interface."""

from abc import ABC, abstractmethod


class ProjectAdapter(ABC):
    """Define project operations used by the application layer."""

    @abstractmethod
    def create_workspace(self, workspace_path: str) -> dict[str, str]:
        """Create a ROS 2 workspace inside the allowed project root."""
        raise NotImplementedError

    @abstractmethod
    def create_package(
        self,
        workspace_path: str,
        package_name: str,
    ) -> dict[str, str]:
        """Create a ROS 2 Python package inside a workspace."""
        raise NotImplementedError

    @abstractmethod
    def create_node(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
    ) -> dict[str, str]:
        """Create a Python ROS 2 node inside an existing package."""
        raise NotImplementedError

    @abstractmethod
    def create_launch_file(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
        launch_name: str,
    ) -> dict[str, str]:
        """Create a Python launch file for an existing ROS 2 package."""
        raise NotImplementedError

    @abstractmethod
    def create_parameter_file(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
        parameter_file_name: str,
    ) -> dict[str, str]:
        """Create a ROS 2 parameter YAML file for an existing package."""
        raise NotImplementedError

    @abstractmethod
    def create_tests(
        self,
        workspace_path: str,
        package_name: str,
    ) -> dict[str, str]:
        """Create basic pytest tests for an existing ROS 2 package."""
        raise NotImplementedError
