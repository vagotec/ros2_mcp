"""Subprocess-based implementation of controlled project execution."""

import subprocess

from ros2_mcp.project.execution.adapter import (
    ExecutionAdapter,
    ExecutionResult,
)
from ros2_mcp.project.execution.policy import CommandPolicy
from ros2_mcp.project.filesystem.safe_filesystem import SafeFilesystem


class SubprocessExecutionAdapter(ExecutionAdapter):
    """Execute approved project commands inside the allowed project root."""

    def __init__(
        self,
        filesystem: SafeFilesystem,
        command_policy: CommandPolicy,
    ) -> None:
        """Create the adapter with filesystem and command restrictions."""
        self._filesystem = filesystem
        self._command_policy = command_policy

    def run(
        self,
        command: list[str],
        working_directory: str,
        timeout_sec: float,
    ) -> ExecutionResult:
        """Execute an approved command and capture its process result."""
        self._command_policy.validate(command)

        resolved_working_directory = self._filesystem.resolve_path(
            working_directory
        )

        if not resolved_working_directory.is_dir():
            raise FileNotFoundError(
                f"Working directory does not exist: "
                f"{resolved_working_directory}"
            )

        try:
            completed_process = subprocess.run(
                command,
                cwd=resolved_working_directory,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as error:
            return ExecutionResult(
                command=command,
                working_directory=str(resolved_working_directory),
                return_code=-1,
                stdout=error.stdout or "",
                stderr=error.stderr or "",
                timed_out=True,
            )

        return ExecutionResult(
            command=command,
            working_directory=str(resolved_working_directory),
            return_code=completed_process.returncode,
            stdout=completed_process.stdout,
            stderr=completed_process.stderr,
            timed_out=False,
        )
