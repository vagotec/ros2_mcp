"""Unit tests for the ROS 2 project application service."""

import pytest

from ros2_mcp.application.project.service import ProjectService
from ros2_mcp.project.adapter import ProjectAdapter
from ros2_mcp.project.execution.adapter import ExecutionAdapter, ExecutionResult


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


class FakeExecutionAdapter(ExecutionAdapter):
    """Capture controlled execution requests for unit tests."""

    def __init__(self) -> None:
        """Initialize the captured execution request."""
        self.last_command: list[str] | None = None
        self.last_working_directory: str | None = None
        self.last_timeout_sec: float | None = None

    def run(
        self,
        command: list[str],
        working_directory: str,
        timeout_sec: float,
    ) -> ExecutionResult:
        """Capture the execution request and return a successful result."""
        self.last_command = command
        self.last_working_directory = working_directory
        self.last_timeout_sec = timeout_sec

        return ExecutionResult(
            command=command,
            working_directory=working_directory,
            return_code=0,
            stdout="Build complete",
            stderr="",
            timed_out=False,
        )


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


def test_build_project_builds_complete_workspace() -> None:
    """Verify that build_project creates a full colcon build command."""
    execution_adapter = FakeExecutionAdapter()
    service = ProjectService(
        FakeProjectAdapter(),
        execution_adapter=execution_adapter,
    )

    result = service.build_project(
        workspace_path="demo_ws",
        timeout_sec=60.0,
    )

    assert execution_adapter.last_command == ["colcon", "build"]
    assert execution_adapter.last_working_directory == "demo_ws"
    assert execution_adapter.last_timeout_sec == 60.0

    assert result.return_code == 0
    assert result.timed_out is False


def test_build_project_supports_package_selection() -> None:
    """Verify that build_project can select specific ROS 2 packages."""
    execution_adapter = FakeExecutionAdapter()
    service = ProjectService(
        FakeProjectAdapter(),
        execution_adapter=execution_adapter,
    )

    service.build_project(
        workspace_path="demo_ws",
        timeout_sec=60.0,
        package_names=["demo_pkg", "camera_driver"],
    )

    assert execution_adapter.last_command == [
        "colcon",
        "build",
        "--packages-select",
        "demo_pkg",
        "camera_driver",
    ]


def test_build_project_requires_execution_adapter() -> None:
    """Verify that build_project fails when execution is not configured."""
    service = ProjectService(FakeProjectAdapter())

    with pytest.raises(
        RuntimeError,
        match="Project execution is not configured",
    ):
        service.build_project(
            workspace_path="demo_ws",
            timeout_sec=60.0,
        )


def test_run_tests_runs_complete_workspace_tests() -> None:
    """Verify that run_tests creates a full colcon test command."""
    execution_adapter = FakeExecutionAdapter()
    service = ProjectService(
        FakeProjectAdapter(),
        execution_adapter=execution_adapter,
    )

    result = service.run_tests(
        workspace_path="demo_ws",
        timeout_sec=90.0,
    )

    assert execution_adapter.last_command == ["colcon", "test"]
    assert execution_adapter.last_working_directory == "demo_ws"
    assert execution_adapter.last_timeout_sec == 90.0
    assert result.return_code == 0
    assert result.timed_out is False


def test_run_tests_supports_package_selection() -> None:
    """Verify that run_tests can select specific ROS 2 packages."""
    execution_adapter = FakeExecutionAdapter()
    service = ProjectService(
        FakeProjectAdapter(),
        execution_adapter=execution_adapter,
    )

    service.run_tests(
        workspace_path="demo_ws",
        timeout_sec=90.0,
        package_names=["demo_pkg", "camera_driver"],
    )

    assert execution_adapter.last_command == [
        "colcon",
        "test",
        "--packages-select",
        "demo_pkg",
        "camera_driver",
    ]


def test_run_tests_requires_execution_adapter() -> None:
    """Verify that run_tests fails when execution is not configured."""
    service = ProjectService(FakeProjectAdapter())

    with pytest.raises(
        RuntimeError,
        match="Project execution is not configured",
    ):
        service.run_tests(
            workspace_path="demo_ws",
            timeout_sec=90.0,
        )
