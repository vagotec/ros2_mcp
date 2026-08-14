"""Tests for ROS 2 MCP configuration resolution and loading."""

from pathlib import Path

import pytest

from ros2_mcp.config.settings import (
    CONFIG_ENV_VAR,
    PACKAGED_DEFAULT_CONFIG,
    load_settings,
    resolve_config_path,
)


def _write_test_config(path: Path, timeout: float = 2.5) -> None:
    """Write a complete test configuration."""
    path.write_text(
        f"""
[runtime]
read_topic_timeout_sec = {timeout}

[safety]
protected_topics = ["/test_protected_topic"]
protected_services = ["/test_protected_service"]
protected_parameters = ["test_parameter"]
protected_actions = ["/test_action"]

allowed_process_packages = ["demo_nodes_cpp"]
allowed_launch_packages = ["demo_nodes_cpp"]

max_persistent_publishers = 10
max_managed_processes = 11
max_managed_launches = 12
max_bag_recordings = 13
max_bag_playbacks = 14
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_resolve_config_path_uses_packaged_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the packaged default when no override is configured."""
    monkeypatch.delenv(CONFIG_ENV_VAR, raising=False)

    resolved = resolve_config_path()

    assert resolved == PACKAGED_DEFAULT_CONFIG.resolve()
    assert resolved.is_file()


def test_resolve_config_path_prefers_explicit_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prefer an explicit function argument over the environment."""
    explicit_config = tmp_path / "explicit.toml"
    environment_config = tmp_path / "environment.toml"

    _write_test_config(explicit_config, timeout=2.0)
    _write_test_config(environment_config, timeout=3.0)

    monkeypatch.setenv(
        CONFIG_ENV_VAR,
        str(environment_config),
    )

    resolved = resolve_config_path(explicit_config)

    assert resolved == explicit_config.resolve()


def test_resolve_config_path_uses_environment_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use ROS2_MCP_CONFIG when no explicit path is supplied."""
    config_path = tmp_path / "environment.toml"
    _write_test_config(config_path)

    monkeypatch.setenv(
        CONFIG_ENV_VAR,
        str(config_path),
    )

    resolved = resolve_config_path()

    assert resolved == config_path.resolve()


def test_resolve_config_path_rejects_missing_explicit_path(
    tmp_path: Path,
) -> None:
    """Reject a missing explicitly supplied configuration file."""
    missing = tmp_path / "missing.toml"

    with pytest.raises(
        FileNotFoundError,
        match="Explicit ROS 2 MCP configuration file was not found",
    ):
        resolve_config_path(missing)


def test_resolve_config_path_rejects_missing_environment_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject an invalid ROS2_MCP_CONFIG override."""
    missing = tmp_path / "missing-environment.toml"

    monkeypatch.setenv(
        CONFIG_ENV_VAR,
        str(missing),
    )

    with pytest.raises(
        FileNotFoundError,
        match="ROS2_MCP_CONFIG points to a configuration file",
    ):
        resolve_config_path()


def test_load_packaged_default_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load runtime and safety values from the packaged default."""
    monkeypatch.delenv(CONFIG_ENV_VAR, raising=False)

    settings = load_settings(resolve_config_path())

    assert settings.runtime.read_topic_timeout_sec == 1.0

    assert settings.safety.protected_topics == (
        "/rosout",
        "/parameter_events",
    )
    assert settings.safety.protected_services == ()
    assert settings.safety.protected_parameters == ()
    assert settings.safety.protected_actions == ()

    assert settings.safety.allowed_process_packages == ()
    assert settings.safety.allowed_launch_packages == ()

    assert settings.safety.max_persistent_publishers == 32
    assert settings.safety.max_managed_processes == 16
    assert settings.safety.max_managed_launches == 8
    assert settings.safety.max_bag_recordings == 4
    assert settings.safety.max_bag_playbacks == 4


def test_load_custom_settings(
    tmp_path: Path,
) -> None:
    """Load all runtime and safety values from a custom config."""
    config_path = tmp_path / "custom.toml"
    _write_test_config(config_path, timeout=4.5)

    settings = load_settings(config_path)

    assert settings.runtime.read_topic_timeout_sec == 4.5

    assert settings.safety.protected_topics == (
        "/test_protected_topic",
    )
    assert settings.safety.protected_services == (
        "/test_protected_service",
    )
    assert settings.safety.protected_parameters == (
        "test_parameter",
    )
    assert settings.safety.protected_actions == (
        "/test_action",
    )

    assert settings.safety.allowed_process_packages == (
        "demo_nodes_cpp",
    )
    assert settings.safety.allowed_launch_packages == (
        "demo_nodes_cpp",
    )

    assert settings.safety.max_persistent_publishers == 10
    assert settings.safety.max_managed_processes == 11
    assert settings.safety.max_managed_launches == 12
    assert settings.safety.max_bag_recordings == 13
    assert settings.safety.max_bag_playbacks == 14


def test_load_settings_rejects_non_positive_limit(
    tmp_path: Path,
) -> None:
    """Reject safety resource limits that are not positive."""
    config_path = tmp_path / "invalid-limit.toml"
    _write_test_config(config_path)

    content = config_path.read_text(encoding="utf-8")
    content = content.replace(
        "max_managed_processes = 11",
        "max_managed_processes = 0",
    )
    config_path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="max_managed_processes must be greater than zero",
    ):
        load_settings(config_path)


def test_load_packaged_default_http_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load the packaged Streamable HTTP defaults."""
    monkeypatch.delenv(CONFIG_ENV_VAR, raising=False)

    settings = load_settings(resolve_config_path())

    assert settings.http.host == "127.0.0.1"
    assert settings.http.port == 8000
    assert settings.http.path == "/mcp"


def test_legacy_config_uses_safe_http_defaults(
    tmp_path: Path,
) -> None:
    """Keep configurations without an HTTP section compatible."""
    config_path = tmp_path / "legacy.toml"
    _write_test_config(config_path)

    settings = load_settings(config_path)

    assert settings.http.host == "127.0.0.1"
    assert settings.http.port == 8000
    assert settings.http.path == "/mcp"


def test_load_custom_http_settings(
    tmp_path: Path,
) -> None:
    """Load explicit Streamable HTTP settings."""
    config_path = tmp_path / "custom-http.toml"
    _write_test_config(config_path)

    content = config_path.read_text(encoding="utf-8")
    content += """
[http]
host = "127.0.0.1"
port = 8765
path = "/robot-mcp/"
"""

    config_path.write_text(content, encoding="utf-8")

    settings = load_settings(config_path)

    assert settings.http.host == "127.0.0.1"
    assert settings.http.port == 8765
    assert settings.http.path == "/robot-mcp"


def test_load_settings_rejects_invalid_http_port(
    tmp_path: Path,
) -> None:
    """Reject HTTP ports outside the valid TCP range."""
    config_path = tmp_path / "invalid-http.toml"
    _write_test_config(config_path)

    content = config_path.read_text(encoding="utf-8")
    content += """
[http]
host = "127.0.0.1"
port = 70000
path = "/mcp"
"""

    config_path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="port must not exceed 65535",
    ):
        load_settings(config_path)


def test_packaged_http_transport_security_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load safe packaged HTTP transport security defaults."""
    monkeypatch.delenv(CONFIG_ENV_VAR, raising=False)

    settings = load_settings(resolve_config_path())

    assert settings.http.enable_dns_rebinding_protection is True

    assert settings.http.allowed_hosts == (
        "127.0.0.1:8000",
        "localhost:8000",
    )

    assert settings.http.allowed_origins == (
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    )


def test_legacy_config_derives_http_security_defaults(
    tmp_path: Path,
) -> None:
    """Derive safe HTTP security values for legacy configs."""
    config_path = tmp_path / "legacy-security.toml"
    _write_test_config(config_path)

    settings = load_settings(config_path)

    assert settings.http.enable_dns_rebinding_protection is True

    assert settings.http.allowed_hosts == (
        "127.0.0.1:8000",
        "localhost:8000",
    )

    assert settings.http.allowed_origins == (
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    )
