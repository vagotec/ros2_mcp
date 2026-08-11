"""Unit tests for subprocess-based project execution."""

from pathlib import Path

import pytest

from ros2_mcp.project.execution.policy import (
    CommandNotAllowedError,
    CommandPolicy,
)
from ros2_mcp.project.execution.subprocess_adapter import (
    SubprocessExecutionAdapter,
)
from ros2_mcp.project.filesystem.safe_filesystem import (
    PathOutsideAllowedRootError,
    SafeFilesystem,
)


def create_adapter(tmp_path: Path) -> SubprocessExecutionAdapter:
    """Create an execution adapter restricted to a temporary root."""
    return SubprocessExecutionAdapter(
        filesystem=SafeFilesystem(tmp_path),
        command_policy=CommandPolicy(),
    )


def test_reject_unapproved_command(tmp_path: Path) -> None:
    """Verify that execution rejects commands outside the allowlist."""
    adapter = create_adapter(tmp_path)

    with pytest.raises(CommandNotAllowedError):
        adapter.run(
            command=["rm", "-rf", "/"],
            working_directory=".",
            timeout_sec=1.0,
        )


def test_reject_working_directory_outside_allowed_root(
    tmp_path: Path,
) -> None:
    """Verify that execution cannot escape the allowed project root."""
    adapter = create_adapter(tmp_path)

    with pytest.raises(PathOutsideAllowedRootError):
        adapter.run(
            command=["colcon", "build"],
            working_directory="../outside",
            timeout_sec=1.0,
        )


def test_require_existing_working_directory(tmp_path: Path) -> None:
    """Verify that execution requires an existing working directory."""
    adapter = create_adapter(tmp_path)

    with pytest.raises(FileNotFoundError):
        adapter.run(
            command=["colcon", "build"],
            working_directory="missing_ws",
            timeout_sec=1.0,
        )
