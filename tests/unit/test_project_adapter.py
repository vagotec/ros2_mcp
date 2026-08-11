"""Unit tests for the filesystem project adapter."""

from pathlib import Path
import py_compile

from ros2_mcp.project.filesystem.adapter import FilesystemProjectAdapter
from ros2_mcp.project.filesystem.safe_filesystem import SafeFilesystem


def test_create_workspace_creates_src_directory(tmp_path: Path) -> None:
    """Verify that a ROS 2 workspace and src directory are created."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    result = adapter.create_workspace("demo_ws")

    workspace = tmp_path / "demo_ws"
    source_directory = workspace / "src"

    assert workspace.is_dir()
    assert source_directory.is_dir()
    assert result == {
        "workspace": str(workspace.resolve()),
        "src": str(source_directory.resolve()),
    }


def test_create_package_creates_python_package_structure(
    tmp_path: Path,
) -> None:
    """Verify that a minimal ROS 2 Python package is created."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    adapter.create_workspace("demo_ws")

    result = adapter.create_package(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    package_directory = tmp_path / "demo_ws/src/demo_pkg"
    python_package_directory = package_directory / "demo_pkg"

    assert package_directory.is_dir()
    assert python_package_directory.is_dir()
    assert (package_directory / "package.xml").is_file()
    assert (package_directory / "setup.py").is_file()
    assert (package_directory / "resource/demo_pkg").is_file()
    assert (python_package_directory / "__init__.py").is_file()

    assert (package_directory / "setup.cfg").is_file()

    assert result == {
        "package": str(package_directory.resolve()),
        "python_package": str(python_package_directory.resolve()),
        "package_xml": str((package_directory / "package.xml").resolve()),
        "setup_py": str((package_directory / "setup.py").resolve()),
        "setup_cfg": str((package_directory / "setup.cfg").resolve()),
    }


def test_create_node_creates_valid_python_node(tmp_path: Path) -> None:
    """Verify that a syntactically valid ROS 2 Python node is created."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    adapter.create_workspace("demo_ws")
    adapter.create_package(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    result = adapter.create_node(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
    )

    package_directory = tmp_path / "demo_ws/src/demo_pkg"
    node_file = package_directory / "demo_pkg/demo_node.py"

    assert node_file.is_file()
    assert result == {
        "node": str(node_file.resolve()),
        "package": str(package_directory.resolve()),
    }

    py_compile.compile(str(node_file), doraise=True)


def test_create_node_requires_existing_package(tmp_path: Path) -> None:
    """Verify that node creation fails when the package does not exist."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    adapter.create_workspace("demo_ws")

    try:
        adapter.create_node(
            workspace_path="demo_ws",
            package_name="missing_pkg",
            node_name="demo_node",
        )
    except FileNotFoundError as error:
        assert "Python package does not exist" in str(error)
    else:
        raise AssertionError(
            "Node creation succeeded without an existing package."
        )


def test_create_launch_file_creates_valid_launch_file(
    tmp_path: Path,
) -> None:
    """Verify that a valid ROS 2 Python launch file is created."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    adapter.create_workspace("demo_ws")
    adapter.create_package(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )
    adapter.create_node(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
    )

    result = adapter.create_launch_file(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
        launch_name="demo",
    )

    package_directory = tmp_path / "demo_ws/src/demo_pkg"
    launch_file = package_directory / "launch/demo.launch.py"
    setup_py = package_directory / "setup.py"

    assert launch_file.is_file()
    assert result == {
        "launch_file": str(launch_file.resolve()),
        "package": str(package_directory.resolve()),
    }

    py_compile.compile(str(launch_file), doraise=True)

    setup_text = setup_py.read_text()

    assert 'glob("launch/*.launch.py")' in setup_text
    assert '"share/" + package_name + "/launch"' in setup_text


def test_create_parameter_file_creates_ros_parameter_yaml(
    tmp_path: Path,
) -> None:
    """Verify that a ROS 2 parameter YAML file is created."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    adapter.create_workspace("demo_ws")
    adapter.create_package(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    result = adapter.create_parameter_file(
        workspace_path="demo_ws",
        package_name="demo_pkg",
        node_name="demo_node",
        parameter_file_name="demo_params",
    )

    package_directory = tmp_path / "demo_ws/src/demo_pkg"
    parameter_file = package_directory / "config/demo_params.yaml"
    setup_py = package_directory / "setup.py"

    assert parameter_file.is_file()
    assert result == {
        "parameter_file": str(parameter_file.resolve()),
        "package": str(package_directory.resolve()),
    }

    parameter_text = parameter_file.read_text()

    assert "demo_node:" in parameter_text
    assert "ros__parameters:" in parameter_text

    setup_text = setup_py.read_text()

    assert 'glob("config/*.yaml")' in setup_text
    assert '"share/" + package_name + "/config"' in setup_text


def test_create_tests_creates_valid_pytest_file(tmp_path: Path) -> None:
    """Verify that a valid pytest file is created."""
    filesystem = SafeFilesystem(tmp_path)
    adapter = FilesystemProjectAdapter(filesystem)

    adapter.create_workspace("demo_ws")
    adapter.create_package(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    result = adapter.create_tests(
        workspace_path="demo_ws",
        package_name="demo_pkg",
    )

    package_directory = tmp_path / "demo_ws/src/demo_pkg"
    test_file = package_directory / "test/test_package_import.py"

    assert test_file.is_file()
    assert result == {
        "test_file": str(test_file.resolve()),
        "package": str(package_directory.resolve()),
    }

    py_compile.compile(str(test_file), doraise=True)

    test_text = test_file.read_text()

    assert 'def test_package_import() -> None:' in test_text
    assert '__import__("demo_pkg")' in test_text
