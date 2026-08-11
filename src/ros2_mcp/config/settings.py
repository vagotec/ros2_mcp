"""Configuration loading for ROS 2 MCP."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class RuntimeSettings:
    """Runtime configuration values."""

    read_topic_timeout_sec: float


@dataclass(frozen=True)
class ProjectSettings:
    """Project filesystem configuration values."""

    allowed_root: Path


@dataclass(frozen=True)
class ExecutionSettings:
    """Controlled project execution configuration values."""

    build_timeout_sec: float
    test_timeout_sec: float


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    runtime: RuntimeSettings
    project: ProjectSettings
    execution: ExecutionSettings


def load_settings(config_path: Path) -> Settings:
    """Load application settings from a TOML configuration file."""
    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    runtime = data["runtime"]
    project = data["project"]
    execution = data["execution"]

    return Settings(
        runtime=RuntimeSettings(
            read_topic_timeout_sec=float(
                runtime["read_topic_timeout_sec"]
            ),
        ),
        project=ProjectSettings(
            allowed_root=Path(
                project["allowed_root"]
            ).expanduser().resolve(),
        ),
        execution=ExecutionSettings(
            build_timeout_sec=float(
                execution["build_timeout_sec"]
            ),
            test_timeout_sec=float(
                execution["test_timeout_sec"]
            ),
        ),
    )
