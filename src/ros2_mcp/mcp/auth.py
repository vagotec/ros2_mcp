"""Authentication helpers for Streamable HTTP MCP access."""

from mcp.server.auth.provider import AccessToken, TokenVerifier


DEFAULT_REMOTE_SCOPE = "ros2_mcp:access"


class StaticBearerTokenVerifier(TokenVerifier):
    """Verify one configured bearer token for controlled lab access."""

    def __init__(
        self,
        expected_token: str,
        scope: str = DEFAULT_REMOTE_SCOPE,
    ) -> None:
        """Create a verifier for one preconfigured bearer token."""
        self._expected_token = expected_token
        self._scope = scope

    async def verify_token(
        self,
        token: str,
    ) -> AccessToken | None:
        """Return access information when the bearer token is valid."""
        if token != self._expected_token:
            return None

        return AccessToken(
            token=token,
            client_id="ros2-mcp-lab-client",
            scopes=[self._scope],
        )
