"""MCP server entry point for ROS 2 runtime operations."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server import MCPServer
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings

from ros2_mcp.application.runtime.service import RuntimeService
from ros2_mcp.config.settings import (
    Settings,
    load_settings,
    resolve_config_path,
)
from ros2_mcp.mcp.instructions import SERVER_INSTRUCTIONS
from ros2_mcp.mcp.prompts import register_prompts
from ros2_mcp.mcp.resources import register_resources
from ros2_mcp.mcp.runtime_tools import register_runtime_tools
from ros2_mcp.ros.jazzy.adapter import JazzyRosAdapter


@dataclass
class AppContext:
    """Hold application resources for the MCP server lifecycle."""

    ros_adapter: JazzyRosAdapter
    runtime_service: RuntimeService
    settings: Settings


@asynccontextmanager
async def app_lifespan(
    server: MCPServer,
) -> AsyncIterator[AppContext]:
    """Create and clean up ROS 2 runtime resources."""
    settings = load_settings(resolve_config_path())

    ros_adapter = JazzyRosAdapter()
    runtime_service = RuntimeService(ros_adapter)

    try:
        yield AppContext(
            ros_adapter=ros_adapter,
            runtime_service=runtime_service,
            settings=settings,
        )
    finally:
        ros_adapter.close()


def create_server(
    *,
    token_verifier: TokenVerifier | None = None,
    auth: AuthSettings | None = None,
) -> MCPServer:
    """Create and configure the ROS 2 runtime MCP server."""
    server = MCPServer(
        name="ros2-mcp",
        instructions=SERVER_INSTRUCTIONS,
        lifespan=app_lifespan,
        token_verifier=token_verifier,
        auth=auth,
    )

    register_runtime_tools(server)
    register_prompts(server)
    register_resources(server)

    return server


def main() -> None:
    """Run the MCP server using the standard stdio transport."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
