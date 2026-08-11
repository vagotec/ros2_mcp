"""Command policy for controlled project execution."""

import re


class CommandNotAllowedError(ValueError):
    """Raised when a command is not allowed by the execution policy."""


class CommandPolicy:
    """Validate commands against an explicit colcon allowlist."""

    _ALLOWED_VERBS = {
        "build",
        "test",
    }

    _PACKAGE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_-]*$")

    def validate(self, command: list[str]) -> None:
        """Validate an allowed colcon build or test command."""
        if len(command) < 2:
            raise CommandNotAllowedError(
                "Command must contain an executable and a verb."
            )

        if command[0] != "colcon":
            raise CommandNotAllowedError(
                f"Executable is not allowed: {command[0]}"
            )

        if command[1] not in self._ALLOWED_VERBS:
            raise CommandNotAllowedError(
                f"Colcon verb is not allowed: {command[1]}"
            )

        arguments = command[2:]

        if not arguments:
            return

        if arguments[0] != "--packages-select":
            raise CommandNotAllowedError(
                "Only --packages-select is allowed."
            )

        package_names = arguments[1:]

        if not package_names:
            raise CommandNotAllowedError(
                "--packages-select requires at least one package name."
            )

        for package_name in package_names:
            if not self._PACKAGE_NAME_PATTERN.fullmatch(package_name):
                raise CommandNotAllowedError(
                    f"Invalid package name: {package_name}"
                )
