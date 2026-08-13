"""Controlled ROS 2 launch management."""

import shutil
import signal
import subprocess
from pathlib import Path
from uuid import uuid4

from ament_index_python.packages import (
    get_package_share_directory,
)


class LaunchMixin:
    """Manage ROS launch files without exposing arbitrary shell commands."""

    def _init_launch_registry(self) -> None:
        """Initialize the launch registry."""
        self._managed_launches: dict[str, dict[str, object]] = {}

    @staticmethod
    def _launch_snapshot(
        launch_id: str,
        entry: dict[str, object],
    ) -> dict[str, object]:
        """Return structured state for one managed launch process."""
        process = entry["process"]
        return_code = process.poll()

        return {
            "launch_id": launch_id,
            "package": entry["package"],
            "launch_file": entry["launch_file"],
            "launch_arguments": dict(entry["launch_arguments"]),
            "pid": process.pid,
            "running": return_code is None,
            "return_code": return_code,
        }

    def start_ros_launch(
        self,
        package_name: str,
        launch_file: str,
        launch_arguments: dict[str, object] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one installed ROS launch file."""
        # # SAFETY:LaunchMixin:start_ros_launch
        self._validate_launch_limit()
        self._validate_launch_package(package_name.strip())
        package = self._validate_simple_name(
            package_name,
            "package_name",
        )
        launch_name = self._validate_simple_name(
            launch_file,
            "launch_file",
        )

        if not (
            launch_name.endswith(".launch.py")
            or launch_name.endswith(".launch.xml")
            or launch_name.endswith(".launch.yaml")
        ):
            raise ValueError(
                "launch_file must be a ROS launch file."
            )

        share_directory = Path(
            get_package_share_directory(package)
        )
        resolved_launch = (
            share_directory
            / "launch"
            / launch_name
        )

        if not resolved_launch.is_file():
            raise LookupError(
                f"ROS launch file not found: "
                f"{package}/{launch_name}"
            )

        ros2 = shutil.which("ros2")

        if ros2 is None:
            raise RuntimeError(
                "ros2 executable was not found in PATH."
            )

        normalized_arguments: dict[str, str] = {}

        for key, value in (
            launch_arguments or {}
        ).items():
            normalized_key = self._validate_simple_name(
                str(key),
                "launch argument name",
            )
            normalized_value = str(value)

            if (
                "\x00" in normalized_value
                or "\n" in normalized_value
                or "\r" in normalized_value
            ):
                raise ValueError(
                    "Launch argument values must not contain "
                    "NUL or newline characters."
                )

            normalized_arguments[
                normalized_key
            ] = normalized_value

        command = [
            ros2,
            "launch",
            package,
            launch_name,
            *[
                f"{key}:={value}"
                for key, value
                in normalized_arguments.items()
            ],
        ]

        if dry_run:
            return {
                "dry_run": True,
                "package": package,
                "launch_file": launch_name,
                "resolved_launch_file": str(
                    resolved_launch
                ),
                "launch_arguments": normalized_arguments,
            }

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        launch_id = uuid4().hex

        self._managed_launches[launch_id] = {
            "process": process,
            "package": package,
            "launch_file": launch_name,
            "launch_arguments": normalized_arguments,
        }

        return self._launch_snapshot(
            launch_id,
            self._managed_launches[launch_id],
        )

    def get_ros_launch(
        self,
        launch_id: str,
    ) -> dict[str, object]:
        """Return one MCP-owned launch process."""
        normalized_id = launch_id.strip().lower()

        entry = self._managed_launches.get(
            normalized_id
        )

        if entry is None:
            raise LookupError(
                f"Managed ROS launch not found: {normalized_id}"
            )

        return self._launch_snapshot(
            normalized_id,
            entry,
        )

    def list_ros_launches(
        self,
    ) -> dict[str, object]:
        """List launch processes started by this MCP server."""
        launches = [
            self._launch_snapshot(launch_id, entry)
            for launch_id, entry
            in sorted(self._managed_launches.items())
        ]

        return {
            "count": len(launches),
            "launches": launches,
        }

    def stop_ros_launch(
        self,
        launch_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one MCP-owned ROS launch process."""
        normalized_id = launch_id.strip().lower()

        entry = self._managed_launches.get(
            normalized_id
        )

        if entry is None:
            raise LookupError(
                f"Managed ROS launch not found: {normalized_id}"
            )

        process = entry["process"]

        if process.poll() is None:
            process.send_signal(signal.SIGINT)

            try:
                process.wait(timeout=timeout_sec)
            except subprocess.TimeoutExpired:
                process.terminate()

                try:
                    process.wait(timeout=timeout_sec)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=timeout_sec)

        result = self._launch_snapshot(
            normalized_id,
            entry,
        )
        result["stopped"] = True

        del self._managed_launches[normalized_id]

        return result

    def _close_ros_launches(self) -> None:
        """Best-effort cleanup of all MCP-owned launch processes."""
        for launch_id in list(
            self._managed_launches
        ):
            try:
                self.stop_ros_launch(
                    launch_id,
                    timeout_sec=1.0,
                )
            except Exception:
                pass
