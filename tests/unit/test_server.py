"""Unit tests for the MCP server entry point."""

from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from pydantic import AnyHttpUrl

from ros2_mcp.mcp.auth import StaticBearerTokenVerifier
from ros2_mcp.server import create_server


def test_create_server_returns_mcp_server() -> None:
    """Verify that the server factory creates an MCPServer instance."""
    server = create_server()

    assert isinstance(server, MCPServer)


def test_create_server_accepts_http_auth_configuration() -> None:
    """Verify that HTTP auth can be supplied without duplicating setup."""
    verifier = StaticBearerTokenVerifier(
        "test-token",
    )

    auth = AuthSettings(
        issuer_url=AnyHttpUrl(
            "https://auth.example.test"
        ),
        resource_server_url=AnyHttpUrl(
            "http://127.0.0.1:8000/mcp"
        ),
        required_scopes=[
            "ros2_mcp:access",
        ],
    )

    server = create_server(
        token_verifier=verifier,
        auth=auth,
    )

    assert isinstance(server, MCPServer)
