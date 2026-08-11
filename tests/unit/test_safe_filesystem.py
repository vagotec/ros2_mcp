"""Unit tests for restricted project filesystem access."""

from pathlib import Path

import pytest

from ros2_mcp.project.filesystem.safe_filesystem import (
    PathOutsideAllowedRootError,
    SafeFilesystem,
)


def test_resolve_relative_path_inside_allowed_root(tmp_path: Path) -> None:
    """Verify that a relative path resolves inside the allowed root."""
    filesystem = SafeFilesystem(tmp_path)

    result = filesystem.resolve_path("workspace/src")

    assert result == (tmp_path / "workspace/src").resolve()


def test_resolve_absolute_path_inside_allowed_root(tmp_path: Path) -> None:
    """Verify that an absolute path inside the allowed root is accepted."""
    filesystem = SafeFilesystem(tmp_path)
    requested_path = tmp_path / "workspace"

    result = filesystem.resolve_path(requested_path)

    assert result == requested_path.resolve()


def test_reject_parent_traversal_outside_allowed_root(tmp_path: Path) -> None:
    """Verify that parent traversal cannot escape the allowed root."""
    filesystem = SafeFilesystem(tmp_path)

    with pytest.raises(PathOutsideAllowedRootError):
        filesystem.resolve_path("../outside")


def test_reject_absolute_path_outside_allowed_root(tmp_path: Path) -> None:
    """Verify that an unrelated absolute path is rejected."""
    filesystem = SafeFilesystem(tmp_path)

    with pytest.raises(PathOutsideAllowedRootError):
        filesystem.resolve_path("/tmp/outside")


def test_reject_symlink_that_points_outside_allowed_root(
    tmp_path: Path,
) -> None:
    """Verify that a symlink cannot escape the allowed root."""
    allowed_root = tmp_path / "allowed"
    outside_root = tmp_path / "outside"

    allowed_root.mkdir()
    outside_root.mkdir()

    escape_link = allowed_root / "escape"
    escape_link.symlink_to(outside_root, target_is_directory=True)

    filesystem = SafeFilesystem(allowed_root)

    with pytest.raises(PathOutsideAllowedRootError):
        filesystem.resolve_path("escape/project")
