"""MCP server entry point for ROS 2 MCP."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from mcp.server import MCPServer

from ros2_mcp.application.project.service import ProjectService
from ros2_mcp.application.runtime.service import RuntimeService
from ros2_mcp.config.settings import Settings, load_settings
from ros2_mcp.mcp.project_tools import register_project_tools
from ros2_mcp.mcp.runtime_tools import register_runtime_tools
from ros2_mcp.project.filesystem.adapter import FilesystemProjectAdapter
from ros2_mcp.project.filesystem.safe_filesystem import SafeFilesystem
from ros2_mcp.ros.jazzy.adapter import JazzyRosAdapter


@dataclass
class AppContext:
    """Hold application resources for the MCP server lifecycle."""

    ros_adapter: JazzyRosAdapter
    runtime_service: RuntimeService
    project_service: ProjectService
    settings: Settings


@asynccontextmanager
async def app_lifespan(server: MCPServer) -> AsyncIterator[AppContext]:
    """Create and clean up application resources."""
    settings = load_settings(Path("config/ros2_mcp.toml"))

    ros_adapter = JazzyRosAdapter()
    runtime_service = RuntimeService(ros_adapter)

    filesystem = SafeFilesystem(settings.project.allowed_root)
    project_adapter = FilesystemProjectAdapter(filesystem)
    project_service = ProjectService(project_adapter)

    try:
        yield AppContext(
            ros_adapter=ros_adapter,
            runtime_service=runtime_service,
            project_service=project_service,
            settings=settings,
        )
    finally:
        ros_adapter.close()


def create_server() -> MCPServer:
    """Create and configure the MCP server."""
    server = MCPServer(
        name="ros2-mcp",
        lifespan=app_lifespan,
    )

    register_runtime_tools(server)
    register_project_tools(server)

    return server


def main() -> None:
    """Run the MCP server using the standard stdio transport."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
