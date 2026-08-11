"""Create a persistent ROS 2 demo project through the MCP server."""

import asyncio

from mcp import Client

from ros2_mcp.server import create_server


async def call_tool_checked(
    client: Client,
    tool_name: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    """Call an MCP tool and fail immediately when the tool reports an error."""
    result = await client.call_tool(tool_name, arguments)

    if result.is_error:
        error_text = " ".join(
            content.text
            for content in result.content
            if hasattr(content, "text")
        )
        raise RuntimeError(
            f"MCP tool '{tool_name}' failed: {error_text}"
        )

    if result.structured_content is None:
        raise RuntimeError(
            f"MCP tool '{tool_name}' returned no structured content."
        )

    return result.structured_content


async def main() -> None:
    """Create, build, and test a complete demo workspace through MCP."""
    server = create_server()

    async with Client(server, raise_exceptions=True) as client:
        print("--- Available project tools ---")
        tools_result = await client.list_tools()
        tool_names = [tool.name for tool in tools_result.tools]

        required_tools = [
            "create_workspace",
            "create_package",
            "create_node",
            "create_launch_file",
            "create_parameter_file",
            "create_tests",
            "build_project",
            "run_tests",
        ]

        for tool_name in required_tools:
            if tool_name not in tool_names:
                raise RuntimeError(f"Missing MCP tool: {tool_name}")

            print(f"{tool_name}: OK")

        print("\n--- Create workspace ---")
        result = await call_tool_checked(
            client,
            "create_workspace",
            {
                "workspace_path": "demo_ws",
            },
        )
        print(result)

        print("\n--- Create package ---")
        result = await call_tool_checked(
            client,
            "create_package",
            {
                "workspace_path": "demo_ws",
                "package_name": "demo_robot",
            },
        )
        print(result)

        print("\n--- Create node ---")
        result = await call_tool_checked(
            client,
            "create_node",
            {
                "workspace_path": "demo_ws",
                "package_name": "demo_robot",
                "node_name": "demo_node",
            },
        )
        print(result)

        print("\n--- Create launch file ---")
        result = await call_tool_checked(
            client,
            "create_launch_file",
            {
                "workspace_path": "demo_ws",
                "package_name": "demo_robot",
                "node_name": "demo_node",
                "launch_name": "demo",
            },
        )
        print(result)

        print("\n--- Create parameter file ---")
        result = await call_tool_checked(
            client,
            "create_parameter_file",
            {
                "workspace_path": "demo_ws",
                "package_name": "demo_robot",
                "node_name": "demo_node",
                "parameter_file_name": "demo_params",
            },
        )
        print(result)

        print("\n--- Create tests ---")
        result = await call_tool_checked(
            client,
            "create_tests",
            {
                "workspace_path": "demo_ws",
                "package_name": "demo_robot",
            },
        )
        print(result)

        print("\n--- Build through MCP ---")
        result = await call_tool_checked(
            client,
            "build_project",
            {
                "workspace_path": "demo_ws",
                "package_names": ["demo_robot"],
            },
        )
        print(result)

        if result["return_code"] != 0:
            raise RuntimeError("MCP build failed.")

        print("\n--- Test through MCP ---")
        result = await call_tool_checked(
            client,
            "run_tests",
            {
                "workspace_path": "demo_ws",
                "package_names": ["demo_robot"],
            },
        )
        print(result)

        if result["return_code"] != 0:
            raise RuntimeError("MCP tests failed.")


if __name__ == "__main__":
    asyncio.run(main())
