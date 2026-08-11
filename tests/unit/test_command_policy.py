"""Unit tests for the project command policy."""

import pytest

from ros2_mcp.project.execution.policy import (
    CommandNotAllowedError,
    CommandPolicy,
)


def test_allow_colcon_build() -> None:
    """Verify that colcon build is allowed."""
    policy = CommandPolicy()

    policy.validate(["colcon", "build"])


def test_allow_colcon_test() -> None:
    """Verify that colcon test is allowed."""
    policy = CommandPolicy()

    policy.validate(["colcon", "test"])


def test_allow_package_selection() -> None:
    """Verify that package selection is allowed."""
    policy = CommandPolicy()

    policy.validate(
        [
            "colcon",
            "build",
            "--packages-select",
            "demo_pkg",
            "camera_driver",
        ]
    )


@pytest.mark.parametrize(
    "command",
    [
        ["rm", "-rf", "/"],
        ["colcon", "list"],
        ["colcon"],
        ["colcon", "build", "--base-paths", "/tmp"],
        ["colcon", "build", "--build-base", "/tmp/build"],
        ["colcon", "build", "--install-base", "/tmp/install"],
        ["colcon", "test", "--test-result-base", "/tmp/results"],
        ["colcon", "build", "--packages-select"],
        ["colcon", "build", "--packages-select", "../outside"],
        ["colcon", "build", "--packages-select", "demo;rm"],
    ],
)
def test_reject_unapproved_commands(command: list[str]) -> None:
    """Verify that unsafe or unsupported commands are rejected."""
    policy = CommandPolicy()

    with pytest.raises(CommandNotAllowedError):
        policy.validate(command)
