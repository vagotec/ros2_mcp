"""Integration tests for ROS 2 project tools through MCP."""

import asyncio
from pathlib import Path
import py_compile
import shutil

from mcp import Client

from ros2_mcp.server import create_server


TEST_WORKSPACE = ".mcp_test_workspace"
TEST_PACKAGE = "demo_pkg"
TEST_NODE = "demo_node"
TEST_LAUNCH = "demo"
TEST_PARAMETER_FILE = "demo_params"


async def call_project_tools() -> None:
    """Verify project creation and filesystem boundary enforcement."""
    server = create_server()
    workspace_path = Path(TEST_WORKSPACE)

    if workspace_path.exists():
        shutil.rmtree(workspace_path)

    try:
        async with Client(server, raise_exceptions=True) as client:
            tools_result = await client.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]

            assert "create_workspace" in tool_names
            assert "create_package" in tool_names
            assert "create_node" in tool_names
            assert "create_launch_file" in tool_names
            assert "create_parameter_file" in tool_names
            assert "create_tests" in tool_names

            workspace_result = await client.call_tool(
                "create_workspace",
                {"workspace_path": TEST_WORKSPACE},
            )
            assert workspace_result.is_error is False

            package_result = await client.call_tool(
                "create_package",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_name": TEST_PACKAGE,
                },
            )
            assert package_result.is_error is False

            node_result = await client.call_tool(
                "create_node",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_name": TEST_PACKAGE,
                    "node_name": TEST_NODE,
                },
            )
            assert node_result.is_error is False

            launch_result = await client.call_tool(
                "create_launch_file",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_name": TEST_PACKAGE,
                    "node_name": TEST_NODE,
                    "launch_name": TEST_LAUNCH,
                },
            )
            assert launch_result.is_error is False

            parameter_result = await client.call_tool(
                "create_parameter_file",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_name": TEST_PACKAGE,
                    "node_name": TEST_NODE,
                    "parameter_file_name": TEST_PARAMETER_FILE,
                },
            )
            assert parameter_result.is_error is False

            tests_result = await client.call_tool(
                "create_tests",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_name": TEST_PACKAGE,
                },
            )
            assert tests_result.is_error is False

            package_path = workspace_path / "src" / TEST_PACKAGE
            node_file = package_path / TEST_PACKAGE / f"{TEST_NODE}.py"
            launch_file = package_path / "launch" / f"{TEST_LAUNCH}.launch.py"
            parameter_file = (
                package_path / "config" / f"{TEST_PARAMETER_FILE}.yaml"
            )
            test_file = package_path / "test/test_package_import.py"

            assert node_file.is_file()
            assert launch_file.is_file()
            assert parameter_file.is_file()
            assert test_file.is_file()

            py_compile.compile(str(node_file), doraise=True)
            py_compile.compile(str(launch_file), doraise=True)
            py_compile.compile(str(test_file), doraise=True)

            blocked_result = await client.call_tool(
                "create_workspace",
                {"workspace_path": "../outside_workspace"},
            )

            assert blocked_result.is_error is True

            error_text = " ".join(
                content.text
                for content in blocked_result.content
                if hasattr(content, "text")
            )

            assert "outside the allowed project root" in error_text
    finally:
        if workspace_path.exists():
            shutil.rmtree(workspace_path)


def test_project_tools_through_mcp() -> None:
    """Run the MCP project tools integration test."""
    asyncio.run(call_project_tools())
