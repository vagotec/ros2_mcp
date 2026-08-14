"""Tests for ros2_mcp HTTP bearer token verification."""

import asyncio

from ros2_mcp.mcp.auth import (
    DEFAULT_REMOTE_SCOPE,
    StaticBearerTokenVerifier,
)


async def _verify_valid_token() -> None:
    """Verify that the configured bearer token is accepted."""
    verifier = StaticBearerTokenVerifier(
        "expected-secret",
    )

    result = await verifier.verify_token(
        "expected-secret"
    )

    assert result is not None
    assert result.client_id == "ros2-mcp-lab-client"
    assert result.scopes == [
        DEFAULT_REMOTE_SCOPE
    ]


async def _verify_invalid_token() -> None:
    """Verify that any other bearer token is rejected."""
    verifier = StaticBearerTokenVerifier(
        "expected-secret",
    )

    result = await verifier.verify_token(
        "wrong-secret"
    )

    assert result is None


def test_static_bearer_token_accepts_expected_token() -> None:
    """Accept the configured bearer token."""
    asyncio.run(
        _verify_valid_token()
    )


def test_static_bearer_token_rejects_wrong_token() -> None:
    """Reject an incorrect bearer token."""
    asyncio.run(
        _verify_invalid_token()
    )
