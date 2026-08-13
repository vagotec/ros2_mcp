"""Controlled ROS 2 process management."""

import os
import signal
import subprocess
from uuid import uuid4

from ros2pkg.api import get_executable_paths


class ProcessMixin:
    """Manage ROS executables without exposing arbitrary shell execution."""

    def _init_process_registry(self) -> None:
        """Initialize the managed ROS process registry."""
        self._managed_ros_processes: dict[str, dict[str, object]] = {}

    @staticmethod
    def _process_snapshot(
        process_id: str,
        entry: dict[str, object],
    ) -> dict[str, object]:
        """Return structured state for one managed process."""
        process = entry["process"]
        return_code = process.poll()

        return {
            "process_id": process_id,
            "package": entry["package"],
            "executable": entry["executable"],
            "arguments": list(entry["arguments"]),
            "pid": process.pid,
            "running": return_code is None,
            "return_code": return_code,
        }

    def start_ros_process(
        self,
        package_name: str,
        executable: str,
        arguments: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start one installed ROS executable."""
        # # SAFETY:ProcessMixin:start_ros_process
        self._validate_process_limit()
        self._validate_process_package(package_name.strip())
        package = self._validate_simple_name(
            package_name,
            "package_name",
        )
        executable_name = self._validate_simple_name(
            executable,
            "executable",
        )
        args = self._validate_process_arguments(arguments)

        executable_paths = get_executable_paths(
            package_name=package
        )

        matching = [
            path
            for path in executable_paths
            if os.path.basename(path) == executable_name
        ]

        if not matching:
            raise LookupError(
                f"ROS executable not found: "
                f"{package}/{executable_name}"
            )

        executable_path = matching[0]
        command = [
            executable_path,
            *args,
        ]

        if dry_run:
            return {
                "dry_run": True,
                "package": package,
                "executable": executable_name,
                "arguments": args,
                "resolved_executable": executable_path,
            }

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        process_id = uuid4().hex

        self._managed_ros_processes[process_id] = {
            "process": process,
            "package": package,
            "executable": executable_name,
            "arguments": args,
        }

        return self._process_snapshot(
            process_id,
            self._managed_ros_processes[process_id],
        )

    def get_ros_process(
        self,
        process_id: str,
    ) -> dict[str, object]:
        """Return one managed ROS process."""
        normalized_id = process_id.strip().lower()

        entry = self._managed_ros_processes.get(
            normalized_id
        )

        if entry is None:
            raise LookupError(
                f"Managed ROS process not found: {normalized_id}"
            )

        return self._process_snapshot(
            normalized_id,
            entry,
        )

    def list_ros_processes(
        self,
    ) -> dict[str, object]:
        """List processes started by this MCP server."""
        processes = [
            self._process_snapshot(process_id, entry)
            for process_id, entry
            in sorted(self._managed_ros_processes.items())
        ]

        return {
            "count": len(processes),
            "processes": processes,
        }

    def stop_ros_process(
        self,
        process_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one process previously started by this MCP server."""
        normalized_id = process_id.strip().lower()

        entry = self._managed_ros_processes.get(
            normalized_id
        )

        if entry is None:
            raise LookupError(
                f"Managed ROS process not found: {normalized_id}"
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

        result = self._process_snapshot(
            normalized_id,
            entry,
        )
        result["stopped"] = True

        del self._managed_ros_processes[normalized_id]

        return result

    def _close_ros_processes(self) -> None:
        """Best-effort cleanup of all MCP-owned ROS processes."""
        for process_id in list(
            self._managed_ros_processes
        ):
            try:
                self.stop_ros_process(
                    process_id,
                    timeout_sec=1.0,
                )
            except Exception:
                pass
