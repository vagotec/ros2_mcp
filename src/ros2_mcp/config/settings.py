"""Configuration loading for ROS 2 MCP."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class RuntimeSettings:
    """Runtime configuration values."""

    read_topic_timeout_sec: float


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    runtime: RuntimeSettings


def load_settings(config_path: Path) -> Settings:
    """Load application settings from a TOML configuration file."""
    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    runtime = data["runtime"]

    return Settings(
        runtime=RuntimeSettings(
            read_topic_timeout_sec=float(runtime["read_topic_timeout_sec"]),
        )
    )
