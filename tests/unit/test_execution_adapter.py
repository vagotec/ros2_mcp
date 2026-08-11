"""Unit tests for project execution abstractions."""

from dataclasses import FrozenInstanceError

import pytest

from ros2_mcp.project.execution.adapter import (
    ExecutionAdapter,
    ExecutionResult,
)


def test_execution_adapter_is_abstract() -> None:
    """Verify that ExecutionAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ExecutionAdapter()


def test_execution_result_stores_process_information() -> None:
    """Verify that ExecutionResult stores command execution details."""
    result = ExecutionResult(
        command=["colcon", "build"],
        working_directory="/allowed/demo_ws",
        return_code=0,
        stdout="Build complete",
        stderr="",
        timed_out=False,
    )

    assert result.command == ["colcon", "build"]
    assert result.working_directory == "/allowed/demo_ws"
    assert result.return_code == 0
    assert result.stdout == "Build complete"
    assert result.stderr == ""
    assert result.timed_out is False


def test_execution_result_is_immutable() -> None:
    """Verify that execution results cannot be modified after creation."""
    result = ExecutionResult(
        command=["colcon", "build"],
        working_directory="/allowed/demo_ws",
        return_code=0,
        stdout="",
        stderr="",
        timed_out=False,
    )

    with pytest.raises(FrozenInstanceError):
        result.return_code = 1
