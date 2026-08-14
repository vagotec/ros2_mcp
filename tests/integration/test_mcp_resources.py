"""Integration tests for modular ROS 2 MCP resources."""

import asyncio
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from urllib.parse import quote

from mcp import Client
from mcp.server import MCPServer

from ros2_mcp.mcp.resources import register_resources
from ros2_mcp.server import create_server


EXPECTED_TOOL_COUNT = 46
EXPECTED_PROMPT_COUNT = 6

EXPECTED_RESOURCE_TEMPLATES = {
    "ros2://runtime/health/{scope}",
    "ros2://runtime/safety/{scope}",
    "ros2://graph/nodes/{scope}",
    "ros2://graph/topics/{scope}",
    "ros2://graph/services/{scope}",
    "ros2://graph/actions/{scope}",
    "ros2://node/{node_name}",
    "ros2://topic/{topic_name}",
    "ros2://action/{action_name}",
}


class FakeRuntimeService:
    """Provide deterministic runtime data for MCP resource tests."""

    def get_runtime_health(
        self,
        timeout_sec: float,
    ) -> dict[str, object]:
        return {
            "status": "ok",
            "timeout_sec": timeout_sec,
        }

    def get_safety_guardrails(self) -> dict[str, object]:
        return {
            "arbitrary_shell": False,
        }

    def list_nodes(self) -> list[str]:
        return [
            "/camera",
            "/controller",
        ]

    def list_topics(self) -> list[tuple[str, list[str]]]:
        return [
            (
                "/camera/image_raw",
                ["sensor_msgs/msg/Image"],
            ),
        ]

    def list_services(self) -> list[tuple[str, list[str]]]:
        return [
            (
                "/camera/get_parameters",
                ["rcl_interfaces/srv/GetParameters"],
            ),
        ]

    def list_actions(self) -> list[tuple[str, list[str]]]:
        return [
            (
                "/navigate_to_pose",
                ["nav2_msgs/action/NavigateToPose"],
            ),
        ]

    def node_info(
        self,
        node_name: str,
    ) -> dict[str, object]:
        return {
            "node_name": node_name,
            "found": True,
        }

    def topic_info(
        self,
        topic_name: str,
    ) -> dict[str, object]:
        return {
            "topic_name": topic_name,
            "found": True,
        }

    def action_info(
        self,
        action_name: str,
    ) -> dict[str, object]:
        return {
            "action_name": action_name,
            "found": True,
        }


@asynccontextmanager
async def fake_lifespan(server: MCPServer):
    """Provide deterministic application state for MCP resource tests."""
    yield SimpleNamespace(
        runtime_service=FakeRuntimeService(),
        settings=SimpleNamespace(
            runtime=SimpleNamespace(
                read_topic_timeout_sec=1.25,
            ),
        ),
    )


def create_resource_test_server() -> MCPServer:
    """Create an MCP server containing only Phase 12 resources."""
    server = MCPServer(
        name="phase12-resource-test",
        lifespan=fake_lifespan,
    )

    register_resources(server)

    return server


async def _verify_resource_inventory() -> None:
    """Verify resources coexist with existing tools and prompts."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        tools = await client.list_tools()
        prompts = await client.list_prompts()
        resources = await client.list_resources()
        templates = await client.list_resource_templates()

        template_uris = {
            item.uri_template
            for item in templates.resource_templates
        }

        assert client.protocol_version == "2026-07-28"
        assert len(tools.tools) == EXPECTED_TOOL_COUNT
        assert len(prompts.prompts) == EXPECTED_PROMPT_COUNT

        # Context-backed runtime resources are intentionally templates.
        assert len(resources.resources) == 0
        assert template_uris == EXPECTED_RESOURCE_TEMPLATES


async def _verify_snapshot_resources() -> None:
    """Verify the six current runtime snapshot resources."""
    server = create_resource_test_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        uris = (
            "ros2://runtime/health/current",
            "ros2://runtime/safety/current",
            "ros2://graph/nodes/current",
            "ros2://graph/topics/current",
            "ros2://graph/services/current",
            "ros2://graph/actions/current",
        )

        results: dict[str, object] = {}

        for uri in uris:
            result = await client.read_resource(uri)

            assert result.contents

            text = result.contents[0].text
            results[uri] = json.loads(text)

        assert results["ros2://runtime/health/current"]["status"] == "ok"
        assert (
            results["ros2://runtime/health/current"]["timeout_sec"]
            == 1.25
        )

        assert (
            results["ros2://runtime/safety/current"]["arbitrary_shell"]
            is False
        )

        assert results["ros2://graph/nodes/current"]["nodes"] == [
            "/camera",
            "/controller",
        ]

        assert "topics" in results["ros2://graph/topics/current"]
        assert "services" in results["ros2://graph/services/current"]
        assert "actions" in results["ros2://graph/actions/current"]


async def _verify_entity_resources() -> None:
    """Verify encoded absolute ROS names survive resource templates."""
    server = create_resource_test_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        cases = (
            (
                "node",
                "/robot1/camera",
                "node_name",
            ),
            (
                "topic",
                "/robot1/camera/image_raw",
                "topic_name",
            ),
            (
                "action",
                "/robot1/navigate_to_pose",
                "action_name",
            ),
        )

        for resource_kind, ros_name, result_key in cases:
            encoded = quote(
                ros_name,
                safe="",
            )

            uri = f"ros2://{resource_kind}/{encoded}"

            result = await client.read_resource(uri)

            assert result.contents

            payload = json.loads(
                result.contents[0].text
            )

            assert payload[result_key] == ros_name
            assert payload["found"] is True


async def _verify_invalid_scope_is_rejected() -> None:
    """Verify snapshot resources accept only the current scope."""
    server = create_resource_test_server()

    async with Client(
        server,
        raise_exceptions=True,
        mode="2026-07-28",
    ) as client:
        try:
            await client.read_resource(
                "ros2://graph/nodes/future",
            )
        except Exception:
            return

        raise AssertionError(
            "Invalid resource scope was unexpectedly accepted."
        )


def test_resource_inventory() -> None:
    """Verify MCP resource inventory and capability coexistence."""
    asyncio.run(
        _verify_resource_inventory()
    )


def test_snapshot_resources() -> None:
    """Verify current ROS 2 snapshot resources."""
    asyncio.run(
        _verify_snapshot_resources()
    )


def test_entity_resources_preserve_ros_names() -> None:
    """Verify entity resources preserve absolute namespaced ROS names."""
    asyncio.run(
        _verify_entity_resources()
    )


def test_invalid_resource_scope_is_rejected() -> None:
    """Verify unsupported snapshot scopes are rejected."""
    asyncio.run(
        _verify_invalid_scope_is_rejected()
    )
