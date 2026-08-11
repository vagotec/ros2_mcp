"""Unit tests for the ROS 2 project application service."""

from ros2_mcp.application.project.service import ProjectService
from ros2_mcp.project.adapter import ProjectAdapter


class FakeProjectAdapter(ProjectAdapter):
    """Provide deterministic project operations for unit tests."""

    def create_workspace(self, workspace_path: str) -> dict[str, str]:
        """Return fixed workspace information."""
        return {
            "workspace": f"/allowed/{workspace_path}",
            "src": f"/allowed/{workspace_path}/src",
        }

    def create_package(
        self,
        workspace_path: str,
        package_name: str,
    ) -> dict[str, str]:
        """Return fixed package information."""
        package_path = f"/allowed/{workspace_path}/src/{package_name}"

        return {
            "package": package_path,
            "python_package": f"{package_path}/{package_name}",
            "package_xml": f"{package_path}/package.xml",
            "setup_py": f"{package_path}/setup.py",
        }

    def create_node(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
    ) -> dict[str, str]:
        """Return fixed node information."""
        package_path = f"/allowed/{workspace_path}/src/{package_name}"

        return {
            "node": f"{package_path}/{package_name}/{node_name}.py",
            "package": package_path,
        }

    def create_launch_file(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
        launch_name: str,
    ) -> dict[str, str]:
        """Return fixed launch file information."""
        package_path = f"/allowed/{workspace_path}/src/{package_name}"

        return {
            "launch_file": f"{package_path}/launch/{launch_name}.launch.py",
            "package": package_path,
        }

    def create_parameter_file(
        self,
        workspace_path: str,
        package_name: str,
        node_name: str,
        parameter_file_name: str,
    ) -> dict[str, str]:
        """Return fixed parameter file information."""
        package_path = f"/allowed/{workspace_path}/src/{package_name}"

        return {
            "parameter_file": (
                f"{package_path}/config/{parameter_file_name}.yaml"
            ),
            "package": package_path,
        }

    def create_tests(
        self,
        workspace_path: str,
        package_name: str,
    ) -> dict[str, str]:
        """Return fixed test file information."""
        package_path = f"/allowed/{workspace_path}/src/{package_name}"

        return {
            "test_file": f"{package_path}/test/test_package_import.py",
            "package": package_path,
        }


def test_create_workspace_uses_project_adapter() -> None:
    """Verify that ProjectService delegates workspace creation."""
    service = ProjectService(FakeProjectAdapter())

    result = service.create_workspace("demo_ws")

    assert result == {
        "workspace": "/allowed/demo_ws",
        "src": "/allowed/demo_ws/src",
    }


def test_create_package_uses_project_adapter() -> None:
    """Verify that ProjectService delegates package creation."""
    service = ProjectService(FakeProjectAdapter())

    result = service.create_package(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    assert result == {
        "package": "/allowed/demo_ws/src/demo_pkg",
        "python_package": "/allowed/demo_ws/src/demo_pkg/demo_pkg",
        "package_xml": "/allowed/demo_ws/src/demo_pkg/package.xml",
        "setup_py": "/allowed/demo_ws/src/demo_pkg/setup.py",
    }


def test_create_node_uses_project_adapter() -> None:
    """Verify that ProjectService delegates node creation."""
    service = ProjectService(FakeProjectAdapter())

    result = service.create_node(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
    )

    assert result == {
        "node": "/allowed/demo_ws/src/demo_pkg/demo_pkg/demo_node.py",
        "package": "/allowed/demo_ws/src/demo_pkg",
    }


def test_create_launch_file_uses_project_adapter() -> None:
    """Verify that ProjectService delegates launch file creation."""
    service = ProjectService(FakeProjectAdapter())

    result = service.create_launch_file(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
        launch_name="demo",
    )

    assert result == {
        "launch_file": "/allowed/demo_ws/src/demo_pkg/launch/demo.launch.py",
        "package": "/allowed/demo_ws/src/demo_pkg",
    }


def test_create_parameter_file_uses_project_adapter() -> None:
    """Verify that ProjectService delegates parameter file creation."""
    service = ProjectService(FakeProjectAdapter())

    result = service.create_parameter_file(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
        parameter_file_name="demo_params",
    )

    assert result == {
        "parameter_file": (
            "/allowed/demo_ws/src/demo_pkg/config/demo_params.yaml"
        ),
        "package": "/allowed/demo_ws/src/demo_pkg",
    }


def test_create_tests_uses_project_adapter() -> None:
    """Verify that ProjectService delegates test creation."""
    service = ProjectService(FakeProjectAdapter())

    result = service.create_tests(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    assert result == {
        "test_file": (
            "/allowed/demo_ws/src/demo_pkg/test/test_package_import.py"
        ),
        "package": "/allowed/demo_ws/src/demo_pkg",
    }
