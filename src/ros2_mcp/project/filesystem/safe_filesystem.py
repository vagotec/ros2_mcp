"""Restricted filesystem access for ROS 2 project operations."""

from pathlib import Path


class PathOutsideAllowedRootError(ValueError):
    """Raised when a requested path escapes the configured project root."""


class SafeFilesystem:
    """Resolve project paths while enforcing an allowed filesystem root."""

    def __init__(self, allowed_root: Path) -> None:
        """Create the filesystem guard for an allowed root."""
        self._allowed_root = allowed_root.expanduser().resolve()

    @property
    def allowed_root(self) -> Path:
        """Return the configured allowed root."""
        return self._allowed_root

    def resolve_path(self, requested_path: str | Path) -> Path:
        """Resolve a requested path and ensure it stays inside the allowed root."""
        path = Path(requested_path).expanduser()

        if path.is_absolute():
            resolved_path = path.resolve()
        else:
            resolved_path = (self._allowed_root / path).resolve()

        if not resolved_path.is_relative_to(self._allowed_root):
            raise PathOutsideAllowedRootError(
                f"Path is outside the allowed project root: {resolved_path}"
            )

        return resolved_path
