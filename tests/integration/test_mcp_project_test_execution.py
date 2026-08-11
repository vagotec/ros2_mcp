"""End-to-end test for ROS 2 build and test execution through MCP."""

import asyncio
from pathlib import Path
import shutil

from mcp import Client

from ros2_mcp.server import create_server


TEST_WORKSPACE = ".mcp_test_execution_workspace"
TEST_PACKAGE = "test_execution_pkg"


async def call_build_and_tests() -> None:
    """Create, build, and test a temporary ROS 2 package through MCP."""
    server = create_server()
    workspace_path = Path(TEST_WORKSPACE)

    if workspace_path.exists():
        shutil.rmtree(workspace_path)

    try:
        async with Client(server, raise_exceptions=True) as client:
            tools_result = await client.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]

            assert "build_project" in tool_names
            assert "run_tests" in tool_names

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

            tests_result = await client.call_tool(
                "create_tests",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_name": TEST_PACKAGE,
                },
            )
            assert tests_result.is_error is False

            build_result = await client.call_tool(
                "build_project",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_names": [TEST_PACKAGE],
                },
            )

            assert build_result.is_error is False
            assert build_result.structured_content is not None
            assert build_result.structured_content["return_code"] == 0
            assert build_result.structured_content["timed_out"] is False

            test_result = await client.call_tool(
                "run_tests",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_names": [TEST_PACKAGE],
                },
            )

            assert test_result.is_error is False
            assert test_result.structured_content is not None
            assert test_result.structured_content["return_code"] == 0
            assert test_result.structured_content["timed_out"] is False
            assert test_result.structured_content["command"] == [
                "colcon",
                "test",
                "--packages-select",
                TEST_PACKAGE,
            ]

            assert (workspace_path / "build").is_dir()
            assert (workspace_path / "install").is_dir()
            assert (workspace_path / "log").is_dir()
    finally:
        if workspace_path.exists():
            shutil.rmtree(workspace_path)


def test_build_and_run_tests_through_mcp() -> None:
    """Run the build and test end-to-end workflow."""
    asyncio.run(call_build_and_tests())
