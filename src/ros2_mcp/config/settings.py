"""Configuration loading for ROS 2 MCP."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


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
class Settings:
    """Application configuration."""

    runtime: RuntimeSettings
    safety: SafetySettings


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


def load_settings(config_path: Path) -> Settings:
    """Load application settings from a TOML configuration file."""
    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    runtime = data["runtime"]
    safety = data["safety"]

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
    )
