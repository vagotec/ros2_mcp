"""Integration tests for authenticated Streamable HTTP MCP access."""

import asyncio
import http.client
import json
import os
import socket

import uvicorn

from mcp import ClientSession
from mcp.client.streamable_http import (
    create_mcp_http_client,
    streamable_http_client,
)

from ros2_mcp.config.settings import (
    HttpSettings,
    Settings,
    load_settings,
    resolve_config_path,
)
from ros2_mcp.http_server import (
    AUTH_ISSUER_ENV_VAR,
    AUTH_TOKEN_ENV_VAR,
    create_http_app,
)


TEST_TOKEN = "phase14-test-token"


def _find_free_port() -> int:
    """Return an available local TCP port."""
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _create_test_settings(port: int) -> Settings:
    """Create isolated authenticated HTTP test settings."""
    base = load_settings(resolve_config_path())

    return Settings(
        runtime=base.runtime,
        safety=base.safety,
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
        "Authenticated HTTP test server did not start."
    )


def _raw_initialize_request(
    port: int,
    token: str | None,
) -> int:
    """Send an initialize request and return the HTTP status."""
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }

    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {
                    "name": "phase14-auth-test",
                    "version": "1.0",
                },
            },
        }
    )

    connection = http.client.HTTPConnection(
        "127.0.0.1",
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
        response.read()

        return response.status
    finally:
        connection.close()


async def _run_auth_server_test(
    test_body,
) -> None:
    """Run one test against an authenticated MCP HTTP server."""
    port = _find_free_port()
    settings = _create_test_settings(port)

    old_token = os.environ.get(AUTH_TOKEN_ENV_VAR)
    old_issuer = os.environ.get(AUTH_ISSUER_ENV_VAR)

    os.environ[AUTH_TOKEN_ENV_VAR] = TEST_TOKEN
    os.environ[AUTH_ISSUER_ENV_VAR] = "https://auth.example.test"

    server = None
    server_task = None

    try:
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

        await _wait_for_server(
            settings.http.host,
            settings.http.port,
        )

        await test_body(
            settings.http.port
        )

    finally:
        if server is not None:
            server.should_exit = True

        if server_task is not None:
            await server_task

        if old_token is None:
            os.environ.pop(
                AUTH_TOKEN_ENV_VAR,
                None,
            )
        else:
            os.environ[AUTH_TOKEN_ENV_VAR] = old_token

        if old_issuer is None:
            os.environ.pop(
                AUTH_ISSUER_ENV_VAR,
                None,
            )
        else:
            os.environ[AUTH_ISSUER_ENV_VAR] = old_issuer


async def _verify_missing_token_is_rejected(
    port: int,
) -> None:
    """Verify that missing bearer authentication returns HTTP 401."""
    status = await asyncio.to_thread(
        _raw_initialize_request,
        port,
        None,
    )

    assert status == 401


async def _verify_wrong_token_is_rejected(
    port: int,
) -> None:
    """Verify that an invalid bearer token returns HTTP 401."""
    status = await asyncio.to_thread(
        _raw_initialize_request,
        port,
        "wrong-token",
    )

    assert status == 401


async def _verify_valid_token_allows_mcp(
    port: int,
) -> None:
    """Verify authenticated MCP operations through Streamable HTTP."""
    url = f"http://127.0.0.1:{port}/mcp"

    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
    }

    async with create_mcp_http_client(
        headers=headers,
    ) as http_client:
        async with streamable_http_client(
            url,
            http_client=http_client,
        ) as streams:
            read_stream, write_stream = streams

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:
                initialized = await session.initialize()

                tools = await session.list_tools()
                prompts = await session.list_prompts()
                templates = await session.list_resource_templates()

                result = await session.call_tool(
                    "get_runtime_health",
                    {},
                )

                assert initialized.protocol_version == "2025-11-25"
                assert len(tools.tools) == 46
                assert len(prompts.prompts) == 6
                assert len(templates.resource_templates) == 9
                assert result.is_error is False


def test_authenticated_http_rejects_missing_token() -> None:
    """Reject HTTP MCP access without a bearer token."""
    asyncio.run(
        _run_auth_server_test(
            _verify_missing_token_is_rejected
        )
    )


def test_authenticated_http_rejects_wrong_token() -> None:
    """Reject HTTP MCP access with an invalid bearer token."""
    asyncio.run(
        _run_auth_server_test(
            _verify_wrong_token_is_rejected
        )
    )


def test_authenticated_http_accepts_valid_token() -> None:
    """Allow authenticated MCP operations with the valid token."""
    asyncio.run(
        _run_auth_server_test(
            _verify_valid_token_allows_mcp
        )
    )

def _raw_unauthenticated_request(
    port: int,
) -> tuple[int, dict[str, str], str]:
    """Send an unauthenticated initialize request and return its response."""
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-07-28",
                "capabilities": {},
                "clientInfo": {
                    "name": "phase14-metadata-test",
                    "version": "1.0",
                },
            },
        }
    )

    connection = http.client.HTTPConnection(
        "127.0.0.1",
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
        response_headers = {
            key.lower(): value
            for key, value in response.getheaders()
        }
        response_body = response.read().decode(
            "utf-8",
            errors="replace",
        )

        return (
            response.status,
            response_headers,
            response_body,
        )
    finally:
        connection.close()


def _raw_metadata_request(
    port: int,
) -> tuple[int, dict[str, object]]:
    """Read the OAuth protected resource metadata document."""
    connection = http.client.HTTPConnection(
        "127.0.0.1",
        port,
        timeout=5,
    )

    try:
        connection.request(
            "GET",
            "/.well-known/oauth-protected-resource/mcp",
            headers={
                "Accept": "application/json",
            },
        )

        response = connection.getresponse()
        body = response.read().decode(
            "utf-8",
            errors="replace",
        )

        return response.status, json.loads(body)
    finally:
        connection.close()


async def _verify_protected_resource_metadata(
    port: int,
) -> None:
    """Verify OAuth protected resource metadata discovery."""
    status, headers, _ = await asyncio.to_thread(
        _raw_unauthenticated_request,
        port,
    )

    assert status == 401

    authenticate = headers.get("www-authenticate")

    assert authenticate is not None
    assert "Bearer" in authenticate
    assert "resource_metadata=" in authenticate
    assert (
        f"http://127.0.0.1:{port}"
        "/.well-known/oauth-protected-resource/mcp"
        in authenticate
    )

    metadata_status, metadata = await asyncio.to_thread(
        _raw_metadata_request,
        port,
    )

    assert metadata_status == 200
    assert metadata["resource"] == (
        f"http://127.0.0.1:{port}/mcp"
    )
    assert metadata["authorization_servers"] == [
        "https://auth.example.test/"
    ]
    assert metadata["scopes_supported"] == [
        "ros2_mcp:access"
    ]
    assert metadata["bearer_methods_supported"] == [
        "header"
    ]


def test_authenticated_http_exposes_protected_resource_metadata() -> None:
    """Expose OAuth protected resource metadata for MCP clients."""
    asyncio.run(
        _run_auth_server_test(
            _verify_protected_resource_metadata
        )
    )
