"""Streamable HTTP entry point for the ROS 2 MCP server."""

import os

from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import AnyHttpUrl
from starlette.applications import Starlette
import uvicorn

from ros2_mcp.config.settings import (
    Settings,
    load_settings,
    resolve_config_path,
)
from ros2_mcp.mcp.auth import (
    DEFAULT_REMOTE_SCOPE,
    StaticBearerTokenVerifier,
)
from ros2_mcp.server import create_server


AUTH_TOKEN_ENV_VAR = "ROS2_MCP_BEARER_TOKEN"
AUTH_ISSUER_ENV_VAR = "ROS2_MCP_AUTH_ISSUER"


def create_transport_security(
    settings: Settings,
) -> TransportSecuritySettings:
    """Create MCP Streamable HTTP transport security settings."""
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=(
            settings.http.enable_dns_rebinding_protection
        ),
        allowed_hosts=list(
            settings.http.allowed_hosts
        ),
        allowed_origins=list(
            settings.http.allowed_origins
        ),
    )


def _resource_server_url(
    settings: Settings,
) -> str:
    """Build the configured MCP HTTP resource URL."""
    return (
        f"http://{settings.http.host}:"
        f"{settings.http.port}"
        f"{settings.http.path}"
    )


def create_http_app(
    settings: Settings | None = None,
) -> Starlette:
    """Create the Streamable HTTP ASGI application."""
    resolved_settings = settings or load_settings(
        resolve_config_path()
    )

    token = os.environ.get(
        AUTH_TOKEN_ENV_VAR,
        "",
    ).strip()

    issuer = os.environ.get(
        AUTH_ISSUER_ENV_VAR,
        "",
    ).strip()

    if token and not issuer:
        raise ValueError(
            f"{AUTH_ISSUER_ENV_VAR} must be set when "
            f"{AUTH_TOKEN_ENV_VAR} is configured."
        )

    if issuer and not token:
        raise ValueError(
            f"{AUTH_TOKEN_ENV_VAR} must be set when "
            f"{AUTH_ISSUER_ENV_VAR} is configured."
        )

    if token:
        server = create_server(
            token_verifier=StaticBearerTokenVerifier(
                token,
            ),
            auth=AuthSettings(
                issuer_url=AnyHttpUrl(
                    issuer
                ),
                resource_server_url=AnyHttpUrl(
                    _resource_server_url(
                        resolved_settings
                    )
                ),
                required_scopes=[
                    DEFAULT_REMOTE_SCOPE,
                ],
            ),
        )
    else:
        server = create_server()

    return server.streamable_http_app(
        streamable_http_path=resolved_settings.http.path,
        json_response=True,
        stateless_http=True,
        transport_security=create_transport_security(
            resolved_settings
        ),
        host=resolved_settings.http.host,
    )


def main() -> None:
    """Run ros2_mcp using the Streamable HTTP transport."""
    settings = load_settings(
        resolve_config_path()
    )

    app = create_http_app(settings)

    uvicorn.run(
        app,
        host=settings.http.host,
        port=settings.http.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
