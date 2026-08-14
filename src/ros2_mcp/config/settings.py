"""Configuration loading for ROS 2 MCP."""

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib


DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_PATH = "/mcp"
DEFAULT_HTTP_DNS_REBINDING_PROTECTION = True


@dataclass(frozen=True)
class RuntimeSettings:
    """Runtime configuration values."""

    read_topic_timeout_sec: float


@dataclass(frozen=True)
class SafetySettings:
    """Safety policy configuration values."""

    protected_topics: tuple[str, ...]
    protected_services: tuple[str, ...]
    protected_parameters: tuple[str, ...]
    protected_actions: tuple[str, ...]

    allowed_process_packages: tuple[str, ...]
    allowed_launch_packages: tuple[str, ...]

    max_persistent_publishers: int
    max_managed_processes: int
    max_managed_launches: int
    max_bag_recordings: int
    max_bag_playbacks: int


@dataclass(frozen=True)
class HttpSettings:
    """Streamable HTTP transport configuration."""

    host: str
    port: int
    path: str
    enable_dns_rebinding_protection: bool
    allowed_hosts: tuple[str, ...]
    allowed_origins: tuple[str, ...]


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    runtime: RuntimeSettings
    safety: SafetySettings
    http: HttpSettings


def _string_tuple(
    section: dict[str, object],
    key: str,
) -> tuple[str, ...]:
    """Read one TOML string list as an immutable tuple."""
    values = section.get(key, [])

    if not isinstance(values, list):
        raise TypeError(
            f"Configuration value {key} must be a list."
        )

    return tuple(
        str(value).strip()
        for value in values
        if str(value).strip()
    )


def _positive_integer(
    section: dict[str, object],
    key: str,
) -> int:
    """Read and validate one positive integer setting."""
    value = int(section[key])

    if value <= 0:
        raise ValueError(
            f"Configuration value {key} must be greater than zero."
        )

    return value


def _http_host(
    section: dict[str, object],
) -> str:
    """Read and validate the HTTP bind host."""
    value = str(
        section.get(
            "host",
            DEFAULT_HTTP_HOST,
        )
    ).strip()

    if not value:
        raise ValueError(
            "Configuration value host must not be empty."
        )

    return value


def _http_port(
    section: dict[str, object],
) -> int:
    """Read and validate the HTTP bind port."""
    value = int(
        section.get(
            "port",
            DEFAULT_HTTP_PORT,
        )
    )

    if value <= 0:
        raise ValueError(
            "Configuration value port must be greater than zero."
        )

    if value > 65535:
        raise ValueError(
            "Configuration value port must not exceed 65535."
        )

    return value


def _http_path(
    section: dict[str, object],
) -> str:
    """Read and validate the MCP HTTP endpoint path."""
    value = str(
        section.get(
            "path",
            DEFAULT_HTTP_PATH,
        )
    ).strip()

    if not value.startswith("/"):
        raise ValueError(
            "Configuration value path must start with '/'."
        )

    if value != "/" and value.endswith("/"):
        value = value.rstrip("/")

    return value


def _http_string_tuple(
    section: dict[str, object],
    key: str,
    fallback: tuple[str, ...],
) -> tuple[str, ...]:
    """Read one optional HTTP string list."""
    if key not in section:
        return fallback

    values = section[key]

    if not isinstance(values, list):
        raise TypeError(
            f"Configuration value {key} must be a list."
        )

    return tuple(
        str(value).strip()
        for value in values
        if str(value).strip()
    )


def _default_allowed_hosts(
    host: str,
    port: int,
) -> tuple[str, ...]:
    """Build safe Host header defaults for local HTTP."""
    hosts = [
        f"{host}:{port}",
    ]

    if host == "127.0.0.1":
        hosts.append(
            f"localhost:{port}"
        )

    return tuple(hosts)


def _default_allowed_origins(
    host: str,
    port: int,
) -> tuple[str, ...]:
    """Build safe Origin header defaults for local HTTP."""
    origins = [
        f"http://{host}:{port}",
    ]

    if host == "127.0.0.1":
        origins.append(
            f"http://localhost:{port}"
        )

    return tuple(origins)


CONFIG_ENV_VAR = "ROS2_MCP_CONFIG"
PACKAGED_DEFAULT_CONFIG = Path(__file__).with_name("default.toml")


def resolve_config_path(
    config_path: Path | None = None,
) -> Path:
    """Resolve an explicit configuration or the packaged default."""
    if config_path is not None:
        resolved = config_path.expanduser().resolve()

        if not resolved.is_file():
            raise FileNotFoundError(
                "Explicit ROS 2 MCP configuration file was not found: "
                f"{resolved}"
            )

        return resolved

    environment_path = os.environ.get(CONFIG_ENV_VAR)

    if environment_path:
        resolved = Path(environment_path).expanduser().resolve()

        if not resolved.is_file():
            raise FileNotFoundError(
                f"{CONFIG_ENV_VAR} points to a configuration file "
                f"that does not exist: {resolved}"
            )

        return resolved

    default_path = PACKAGED_DEFAULT_CONFIG.resolve()

    if default_path.is_file():
        return default_path

    raise FileNotFoundError(
        "Packaged ROS 2 MCP default configuration was not found: "
        f"{default_path}. "
        f"Set {CONFIG_ENV_VAR} to an explicit configuration file."
    )


def load_settings(config_path: Path) -> Settings:
    """Load application settings from a TOML configuration file."""
    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    runtime = data["runtime"]
    safety = data["safety"]

    http_data = data.get(
        "http",
        {},
    )

    if not isinstance(http_data, dict):
        raise TypeError(
            "Configuration section http must be a table."
        )

    host = _http_host(http_data)
    port = _http_port(http_data)

    allowed_hosts = _http_string_tuple(
        http_data,
        "allowed_hosts",
        _default_allowed_hosts(
            host,
            port,
        ),
    )

    allowed_origins = _http_string_tuple(
        http_data,
        "allowed_origins",
        _default_allowed_origins(
            host,
            port,
        ),
    )

    return Settings(
        runtime=RuntimeSettings(
            read_topic_timeout_sec=float(
                runtime["read_topic_timeout_sec"]
            ),
        ),
        safety=SafetySettings(
            protected_topics=_string_tuple(
                safety,
                "protected_topics",
            ),
            protected_services=_string_tuple(
                safety,
                "protected_services",
            ),
            protected_parameters=_string_tuple(
                safety,
                "protected_parameters",
            ),
            protected_actions=_string_tuple(
                safety,
                "protected_actions",
            ),
            allowed_process_packages=_string_tuple(
                safety,
                "allowed_process_packages",
            ),
            allowed_launch_packages=_string_tuple(
                safety,
                "allowed_launch_packages",
            ),
            max_persistent_publishers=_positive_integer(
                safety,
                "max_persistent_publishers",
            ),
            max_managed_processes=_positive_integer(
                safety,
                "max_managed_processes",
            ),
            max_managed_launches=_positive_integer(
                safety,
                "max_managed_launches",
            ),
            max_bag_recordings=_positive_integer(
                safety,
                "max_bag_recordings",
            ),
            max_bag_playbacks=_positive_integer(
                safety,
                "max_bag_playbacks",
            ),
        ),
        http=HttpSettings(
            host=host,
            port=port,
            path=_http_path(http_data),
            enable_dns_rebinding_protection=bool(
                http_data.get(
                    "enable_dns_rebinding_protection",
                    DEFAULT_HTTP_DNS_REBINDING_PROTECTION,
                )
            ),
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        ),
    )
