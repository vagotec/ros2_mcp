"""Integration tests for the Streamable HTTP MCP transport."""

import asyncio
import socket

from mcp import Client
import uvicorn

from ros2_mcp.config.settings import HttpSettings, Settings
from ros2_mcp.http_server import create_http_app
from ros2_mcp.mcp.instructions import SERVER_INSTRUCTIONS
from ros2_mcp.config.settings import load_settings, resolve_config_path


EXPECTED_TOOL_COUNT = 46
EXPECTED_PROMPT_COUNT = 6
EXPECTED_RESOURCE_TEMPLATE_COUNT = 9


def _find_free_port() -> int:
    """Reserve and return an available local TCP port."""
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http_test_settings() -> Settings:
    """Create settings for an isolated local HTTP test server."""
    settings = load_settings(resolve_config_path())
    port = _find_free_port()

    return Settings(
        runtime=settings.runtime,
        safety=settings.safety,
        http=HttpSettings(
            host="127.0.0.1",
            port=port,
            path="/mcp",
            enable_dns_rebinding_protection=True,
            allowed_hosts=(
                f"127.0.0.1:{port}",
                f"localhost:{port}",
            ),
            allowed_origins=(
                f"http://127.0.0.1:{port}",
                f"http://localhost:{port}",
            ),
        ),
    )


async def _wait_for_server(
    host: str,
    port: int,
) -> None:
    """Wait until the local HTTP server accepts connections."""
    for _ in range(100):
        try:
            reader, writer = await asyncio.open_connection(
                host,
                port,
            )
        except OSError:
            await asyncio.sleep(0.05)
            continue

        writer.close()
        await writer.wait_closed()
        return

    raise RuntimeError(
        "Streamable HTTP test server did not start."
    )


async def _verify_streamable_http() -> None:
    """Verify MCP capabilities through real Streamable HTTP."""
    settings = _http_test_settings()
    app = create_http_app(settings)

    config = uvicorn.Config(
        app,
        host=settings.http.host,
        port=settings.http.port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(
        server.serve()
    )

    try:
        await _wait_for_server(
            settings.http.host,
            settings.http.port,
        )

        url = (
            f"http://{settings.http.host}:"
            f"{settings.http.port}"
            f"{settings.http.path}"
        )

        async with Client(
            url,
            mode="auto",
            raise_exceptions=True,
        ) as client:
            tools = await client.list_tools()
            prompts = await client.list_prompts()
            resources = await client.list_resources()
            templates = await client.list_resource_templates()

            assert client.protocol_version == "2026-07-28"

            discover = client.session.discover_result

            assert discover is not None
            assert discover.supported_versions == [
                "2026-07-28"
            ]
            assert discover.instructions == SERVER_INSTRUCTIONS

            assert len(tools.tools) == EXPECTED_TOOL_COUNT
            assert len(prompts.prompts) == EXPECTED_PROMPT_COUNT
            assert len(resources.resources) == 0
            assert (
                len(templates.resource_templates)
                == EXPECTED_RESOURCE_TEMPLATE_COUNT
            )

            tool_result = await client.call_tool(
                "get_runtime_health",
                {},
            )

            assert tool_result.is_error is False
            assert tool_result.content

            resource_result = await client.read_resource(
                "ros2://graph/nodes/current"
            )

            assert resource_result.contents

            prompt_result = await client.get_prompt(
                "ros_health_check"
            )

            assert prompt_result.messages
            assert (
                prompt_result.description
                == "Inspect the ROS 2 runtime and summarize "
                "its overall health."
            )
    finally:
        server.should_exit = True
        await server_task


def test_streamable_http_transport() -> None:
    """Verify the complete MCP baseline through Streamable HTTP."""
    asyncio.run(
        _verify_streamable_http()
    )


async def _send_raw_http_request(
    host: str,
    port: int,
    headers: dict[str, str],
) -> tuple[int, str]:
    """Send one raw HTTP request to the MCP endpoint."""
    import http.client
    import json

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-07-28",
                "capabilities": {},
                "clientInfo": {
                    "name": "transport-security-test",
                    "version": "1.0",
                },
            },
        }
    )

    def send() -> tuple[int, str]:
        connection = http.client.HTTPConnection(
            host,
            port,
            timeout=5,
        )

        try:
            connection.request(
                "POST",
                "/mcp",
                body=body,
                headers=headers,
            )

            response = connection.getresponse()

            return (
                response.status,
                response.read().decode(
                    "utf-8",
                    errors="replace",
                ),
            )
        finally:
            connection.close()

    return await asyncio.to_thread(send)


async def _verify_invalid_origin_is_rejected() -> None:
    """Verify that an untrusted Origin is rejected with HTTP 403."""
    settings = _http_test_settings()
    app = create_http_app(settings)

    config = uvicorn.Config(
        app,
        host=settings.http.host,
        port=settings.http.port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(
        server.serve()
    )

    try:
        await _wait_for_server(
            settings.http.host,
            settings.http.port,
        )

        status, body = await _send_raw_http_request(
            settings.http.host,
            settings.http.port,
            {
                "Accept": (
                    "application/json, "
                    "text/event-stream"
                ),
                "Content-Type": "application/json",
                "Origin": "https://evil.example",
            },
        )

        assert status == 403
        assert "Invalid Origin header" in body

    finally:
        server.should_exit = True
        await server_task


async def _verify_invalid_host_is_rejected() -> None:
    """Verify that an untrusted Host is rejected with HTTP 421."""
    settings = _http_test_settings()
    app = create_http_app(settings)

    config = uvicorn.Config(
        app,
        host=settings.http.host,
        port=settings.http.port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(
        server.serve()
    )

    try:
        await _wait_for_server(
            settings.http.host,
            settings.http.port,
        )

        status, body = await _send_raw_http_request(
            settings.http.host,
            settings.http.port,
            {
                "Accept": (
                    "application/json, "
                    "text/event-stream"
                ),
                "Content-Type": "application/json",
                "Host": "evil.example",
            },
        )

        assert status == 421
        assert "Invalid Host header" in body

    finally:
        server.should_exit = True
        await server_task


def test_streamable_http_rejects_invalid_origin() -> None:
    """Reject untrusted Origin headers."""
    asyncio.run(
        _verify_invalid_origin_is_rejected()
    )


def test_streamable_http_rejects_invalid_host() -> None:
    """Reject untrusted Host headers."""
    asyncio.run(
        _verify_invalid_host_is_rejected()
    )

async def _verify_2026_07_28_request_headers() -> None:
    """Verify MCP 2026-07-28 HTTP request metadata headers."""
    from starlette.middleware.base import BaseHTTPMiddleware

    captured_headers: list[dict[str, str | None]] = []

    class HeaderCaptureMiddleware(BaseHTTPMiddleware):
        """Capture MCP metadata headers from HTTP requests."""

        async def dispatch(self, request, call_next):
            captured_headers.append(
                {
                    "method": request.headers.get("mcp-method"),
                    "name": request.headers.get("mcp-name"),
                    "protocol": request.headers.get(
                        "mcp-protocol-version"
                    ),
                }
            )

            return await call_next(request)

    settings = _http_test_settings()
    app = create_http_app(settings)
    app.add_middleware(HeaderCaptureMiddleware)

    config = uvicorn.Config(
        app,
        host=settings.http.host,
        port=settings.http.port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(
        server.serve()
    )

    try:
        await _wait_for_server(
            settings.http.host,
            settings.http.port,
        )

        url = (
            f"http://{settings.http.host}:"
            f"{settings.http.port}"
            f"{settings.http.path}"
        )

        async with Client(
            url,
            mode="auto",
            raise_exceptions=True,
        ) as client:
            assert client.protocol_version == "2026-07-28"

            await client.list_tools()
            await client.list_prompts()
            await client.list_resource_templates()

            await client.call_tool(
                "get_runtime_health",
                {},
            )

            await client.read_resource(
                "ros2://graph/nodes/current"
            )

            await client.get_prompt(
                "ros_health_check"
            )

        expected_headers = {
            ("server/discover", None),
            ("tools/list", None),
            ("prompts/list", None),
            ("resources/templates/list", None),
            ("tools/call", "get_runtime_health"),
            (
                "resources/read",
                "ros2://graph/nodes/current",
            ),
            ("prompts/get", "ros_health_check"),
        }

        actual_headers = {
            (
                item["method"],
                item["name"],
            )
            for item in captured_headers
        }

        assert expected_headers <= actual_headers

        relevant_headers = [
            item
            for item in captured_headers
            if (
                item["method"],
                item["name"],
            )
            in expected_headers
        ]

        assert relevant_headers

        for item in relevant_headers:
            assert item["protocol"] == "2026-07-28"

    finally:
        server.should_exit = True
        await server_task


def test_streamable_http_sends_2026_07_28_request_headers() -> None:
    """Verify MCP 2026-07-28 HTTP request metadata headers."""
    asyncio.run(
        _verify_2026_07_28_request_headers()
    )
