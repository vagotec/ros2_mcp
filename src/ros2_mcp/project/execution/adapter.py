"""Abstract adapter for controlled project command execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    """Represent the result of a controlled project command."""

    command: list[str]
    working_directory: str
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool


class ExecutionAdapter(ABC):
    """Define controlled command execution for project operations."""

    @abstractmethod
    def run(
        self,
        command: list[str],
        working_directory: str,
        timeout_sec: float,
    ) -> ExecutionResult:
        """Execute an allowed command inside an approved working directory."""
        raise NotImplementedError
