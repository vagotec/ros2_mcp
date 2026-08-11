"""End-to-end integration test for ROS 2 project building through MCP."""

import asyncio
from pathlib import Path
import shutil

from mcp import Client

from ros2_mcp.server import create_server


TEST_WORKSPACE = ".mcp_build_test_workspace"
TEST_PACKAGE = "build_demo_pkg"


async def call_build_project() -> None:
    """Create and build a temporary ROS 2 package through MCP."""
    server = create_server()
    workspace_path = Path(TEST_WORKSPACE)

    if workspace_path.exists():
        shutil.rmtree(workspace_path)

    try:
        async with Client(server, raise_exceptions=True) as client:
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

            build_result = await client.call_tool(
                "build_project",
                {
                    "workspace_path": TEST_WORKSPACE,
                    "package_names": [TEST_PACKAGE],
                },
            )

            assert build_result.is_error is False
            assert build_result.structured_content is not None

            result = build_result.structured_content

            assert result["return_code"] == 0
            assert result["timed_out"] is False
            assert result["command"] == [
                "colcon",
                "build",
                "--packages-select",
                TEST_PACKAGE,
            ]

            assert (workspace_path / "build").is_dir()
            assert (workspace_path / "install").is_dir()
            assert (workspace_path / "log").is_dir()
    finally:
        if workspace_path.exists():
            shutil.rmtree(workspace_path)


def test_build_project_through_mcp() -> None:
    """Run the ROS 2 build end-to-end integration test."""
    asyncio.run(call_build_project())
