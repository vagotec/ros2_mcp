"""Safety helpers for controlled ROS 2 runtime operations."""

import re

from ros2_mcp.config.settings import (
    SafetySettings,
    load_settings,
    resolve_config_path,
)


_SAFE_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")


class SafetyMixin:
    """Provide configurable safety checks for runtime operations."""

    def _init_safety(self) -> None:
        """Load the runtime safety policy from configuration."""
        settings = load_settings(resolve_config_path())

        self._safety_settings: SafetySettings = settings.safety

    @staticmethod
    def _normalize_ros_name(value: str) -> str:
        """Normalize one ROS graph name."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("ROS name must not be empty.")

        if not normalized.startswith("/"):
            normalized = f"/{normalized}"

        return normalized

    @staticmethod
    def _validate_simple_name(
        value: str,
        field_name: str,
    ) -> str:
        """Validate a package, executable, or managed resource name."""
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty."
            )

        if "/" in normalized or "\\" in normalized:
            raise ValueError(
                f"{field_name} must not contain path separators."
            )

        if not _SAFE_NAME.fullmatch(normalized):
            raise ValueError(
                f"{field_name} contains unsupported characters."
            )

        return normalized

    @staticmethod
    def _validate_process_arguments(
        arguments: list[str] | None,
    ) -> list[str]:
        """Validate structured process arguments without using a shell."""
        normalized: list[str] = []

        for argument in arguments or []:
            value = str(argument)

            if (
                "\x00" in value
                or "\n" in value
                or "\r" in value
            ):
                raise ValueError(
                    "Process arguments must not contain "
                    "NUL or newline characters."
                )

            if len(value) > 2048:
                raise ValueError(
                    "Individual process arguments must not "
                    "exceed 2048 characters."
                )

            normalized.append(value)

        if len(normalized) > 128:
            raise ValueError(
                "No more than 128 process arguments are allowed."
            )

        return normalized

    def _validate_topic_write(
        self,
        topic_name: str,
    ) -> None:
        """Reject writes to protected ROS topics."""
        normalized = self._normalize_ros_name(
            topic_name
        )

        if normalized in self._safety_settings.protected_topics:
            raise PermissionError(
                f"Writing to protected ROS topic is blocked: "
                f"{normalized}"
            )

    def _validate_service_write(
        self,
        service_name: str,
    ) -> None:
        """Reject calls to protected ROS services."""
        normalized = self._normalize_ros_name(
            service_name
        )

        if normalized in self._safety_settings.protected_services:
            raise PermissionError(
                f"Calling protected ROS service is blocked: "
                f"{normalized}"
            )

    def _validate_parameter_write(
        self,
        node_name: str,
        parameter_name: str,
    ) -> None:
        """Reject writes to protected ROS parameters."""
        node = self._normalize_ros_name(
            node_name
        )
        parameter = parameter_name.strip()

        candidates = {
            parameter,
            f"{node}:{parameter}",
        }

        if candidates.intersection(
            self._safety_settings.protected_parameters
        ):
            raise PermissionError(
                f"Writing protected ROS parameter is blocked: "
                f"{node}:{parameter}"
            )

    def _validate_action_write(
        self,
        action_name: str,
    ) -> None:
        """Reject goals sent to protected ROS actions."""
        normalized = self._normalize_ros_name(
            action_name
        )

        if normalized in self._safety_settings.protected_actions:
            raise PermissionError(
                f"Sending goal to protected ROS action is blocked: "
                f"{normalized}"
            )

    def _validate_process_package(
        self,
        package_name: str,
    ) -> None:
        """Apply an optional ROS executable package allowlist."""
        allowed = (
            self._safety_settings.allowed_process_packages
        )

        if allowed and package_name not in allowed:
            raise PermissionError(
                f"ROS process package is not allowed: "
                f"{package_name}"
            )

    def _validate_launch_package(
        self,
        package_name: str,
    ) -> None:
        """Apply an optional ROS launch package allowlist."""
        allowed = (
            self._safety_settings.allowed_launch_packages
        )

        if allowed and package_name not in allowed:
            raise PermissionError(
                f"ROS launch package is not allowed: "
                f"{package_name}"
            )

    def _validate_process_limit(self) -> None:
        """Enforce the maximum managed ROS process count."""
        if (
            len(self._managed_ros_processes)
            >= self._safety_settings.max_managed_processes
        ):
            raise RuntimeError(
                "Maximum managed ROS process count reached."
            )

    def _validate_launch_limit(self) -> None:
        """Enforce the maximum managed launch count."""
        if (
            len(self._managed_launches)
            >= self._safety_settings.max_managed_launches
        ):
            raise RuntimeError(
                "Maximum managed ROS launch count reached."
            )

    def _validate_bag_recording_limit(self) -> None:
        """Enforce the maximum concurrent bag recording count."""
        if (
            len(self._bag_recordings)
            >= self._safety_settings.max_bag_recordings
        ):
            raise RuntimeError(
                "Maximum managed bag recording count reached."
            )

    def _validate_bag_playback_limit(self) -> None:
        """Enforce the maximum concurrent bag playback count."""
        if (
            len(self._bag_playbacks)
            >= self._safety_settings.max_bag_playbacks
        ):
            raise RuntimeError(
                "Maximum managed bag playback count reached."
            )

    def _validate_persistent_publisher_create(
        self,
        topic_name: str,
    ) -> None:
        """Validate creation of a persistent ROS publisher."""
        self._validate_topic_write(
            topic_name
        )

        if (
            len(self._persistent_publishers)
            >= self._safety_settings.max_persistent_publishers
        ):
            raise RuntimeError(
                "Maximum persistent publisher count reached."
            )

    def get_safety_guardrails(
        self,
    ) -> dict[str, object]:
        """Return active generic ROS runtime safety properties."""
        return {
            "arbitrary_shell": False,
            "managed_process_stop_only": True,
            "managed_launch_stop_only": True,
            "managed_rosbag_stop_only": True,
            "package_resolution_required": True,
            "launch_file_resolution_required": True,
            "path_traversal_for_managed_names": False,
            "structured_argument_validation": True,
            "protected_topics": sorted(
                self._safety_settings.protected_topics
            ),
            "protected_services": sorted(
                self._safety_settings.protected_services
            ),
            "protected_parameters": sorted(
                self._safety_settings.protected_parameters
            ),
            "protected_actions": sorted(
                self._safety_settings.protected_actions
            ),
            "allowed_process_packages": sorted(
                self._safety_settings.allowed_process_packages
            ),
            "allowed_launch_packages": sorted(
                self._safety_settings.allowed_launch_packages
            ),
            "limits": {
                "persistent_publishers": (
                    self._safety_settings.max_persistent_publishers
                ),
                "managed_processes": (
                    self._safety_settings.max_managed_processes
                ),
                "managed_launches": (
                    self._safety_settings.max_managed_launches
                ),
                "bag_recordings": (
                    self._safety_settings.max_bag_recordings
                ),
                "bag_playbacks": (
                    self._safety_settings.max_bag_playbacks
                ),
            },
            "dry_run_supported": [
                "start_ros_process",
                "start_ros_launch",
                "start_bag_recording",
                "start_bag_playback",
            ],
        }
