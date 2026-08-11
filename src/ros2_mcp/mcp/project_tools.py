"""MCP tools for ROS 2 project operations."""

from dataclasses import asdict
from typing import TYPE_CHECKING

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.types import ToolAnnotations

if TYPE_CHECKING:
    from ros2_mcp.server import AppContext


def register_project_tools(server: MCPServer) -> None:
    """Register ROS 2 project management tools with the MCP server."""

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def create_workspace(
        workspace_path: str,
        ctx: Context["AppContext"],
    ) -> dict[str, str]:
        """Create a ROS 2 workspace inside the configured project root."""
        app_context = ctx.request_context.lifespan_context
        return app_context.project_service.create_workspace(workspace_path)

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def create_package(
        workspace_path: str,
        package_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, str]:
        """Create a ROS 2 Python package inside a workspace."""
        app_context = ctx.request_context.lifespan_context
        return app_context.project_service.create_package(
            workspace_path=workspace_path,
            package_name=package_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def create_node(
        workspace_path: str,
        package_name: str,
        node_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, str]:
        """Create a Python ROS 2 node inside an existing package."""
        app_context = ctx.request_context.lifespan_context
        return app_context.project_service.create_node(
            workspace_path=workspace_path,
            package_name=package_name,
            node_name=node_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def create_launch_file(
        workspace_path: str,
        package_name: str,
        node_name: str,
        launch_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, str]:
        """Create a Python ROS 2 launch file inside an existing package."""
        app_context = ctx.request_context.lifespan_context
        return app_context.project_service.create_launch_file(
            workspace_path=workspace_path,
            package_name=package_name,
            node_name=node_name,
            launch_name=launch_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def create_parameter_file(
        workspace_path: str,
        package_name: str,
        node_name: str,
        parameter_file_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, str]:
        """Create a ROS 2 parameter YAML file inside an existing package."""
        app_context = ctx.request_context.lifespan_context
        return app_context.project_service.create_parameter_file(
            workspace_path=workspace_path,
            package_name=package_name,
            node_name=node_name,
            parameter_file_name=parameter_file_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def create_tests(
        workspace_path: str,
        package_name: str,
        ctx: Context["AppContext"],
    ) -> dict[str, str]:
        """Create basic pytest tests for an existing ROS 2 package."""
        app_context = ctx.request_context.lifespan_context
        return app_context.project_service.create_tests(
            workspace_path=workspace_path,
            package_name=package_name,
        )

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def build_project(
        workspace_path: str,
        ctx: Context["AppContext"],
        package_names: list[str] | None = None,
    ) -> dict[str, object]:
        """Build a ROS 2 workspace or selected packages using colcon."""
        app_context = ctx.request_context.lifespan_context

        result = app_context.project_service.build_project(
            workspace_path=workspace_path,
            timeout_sec=app_context.settings.execution.build_timeout_sec,
            package_names=package_names,
        )

        return asdict(result)

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def run_tests(
        workspace_path: str,
        ctx: Context["AppContext"],
        package_names: list[str] | None = None,
    ) -> dict[str, object]:
        """Run ROS 2 tests for a workspace or selected packages."""
        app_context = ctx.request_context.lifespan_context

        result = app_context.project_service.run_tests(
            workspace_path=workspace_path,
            timeout_sec=app_context.settings.execution.test_timeout_sec,
            package_names=package_names,
        )

        return asdict(result)
