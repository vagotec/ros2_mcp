"""ROS 2 Jazzy interfaces runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class InterfacesMixin:
    """Provide ROS 2 Jazzy interfaces operations."""

    def list_interfaces(
        self,
        interface_kind: str | None,
        package_name: str | None,
    ) -> dict[str, object]:
        """List installed ROS 2 interfaces using rosidl runtime metadata."""
        from rosidl_runtime_py import get_interfaces

        allowed_kinds = {
            "msg",
            "srv",
            "action",
        }

        normalized_kind = None

        if interface_kind is not None:
            stripped_kind = interface_kind.strip().lower()

            if stripped_kind:
                if stripped_kind not in allowed_kinds:
                    raise ValueError(
                        "interface_kind must be msg, srv, action, or None."
                    )

                normalized_kind = stripped_kind

        normalized_package = None

        if package_name is not None:
            stripped_package = package_name.strip()

            if stripped_package:
                normalized_package = stripped_package

        interfaces_by_package = get_interfaces()

        discovered: list[dict[str, str]] = []

        for package, interface_names in interfaces_by_package.items():
            if (
                normalized_package is not None
                and package != normalized_package
            ):
                continue

            for relative_name in interface_names:
                parts = relative_name.split("/", 1)

                if len(parts) != 2:
                    continue

                kind, interface_basename = parts

                if kind not in allowed_kinds:
                    continue

                if (
                    normalized_kind is not None
                    and kind != normalized_kind
                ):
                    continue

                discovered.append(
                    {
                        "name": (
                            f"{package}/{kind}/{interface_basename}"
                        ),
                        "package": package,
                        "kind": kind,
                        "interface": interface_basename,
                    }
                )

        discovered.sort(
            key=lambda item: item["name"]
        )

        counts = {
            "msg": 0,
            "srv": 0,
            "action": 0,
        }

        for item in discovered:
            counts[item["kind"]] += 1

        return {
            "interface_kind": normalized_kind,
            "package_name": normalized_package,
            "count": len(discovered),
            "counts": counts,
            "interfaces": discovered,
        }

    def interface_info(
        self,
        interface_name: str,
    ) -> dict[str, object]:
        """Return field information for one installed ROS 2 interface."""
        from rosidl_runtime_py.utilities import (
            get_action,
            get_message,
            get_service,
        )

        normalized_name = interface_name.strip()

        if not normalized_name:
            raise ValueError(
                "interface_name must not be empty."
            )

        parts = normalized_name.split("/")

        if len(parts) != 3:
            raise ValueError(
                "interface_name must use package/kind/Interface format."
            )

        package_name, interface_kind, short_name = parts

        if not package_name or not short_name:
            raise ValueError(
                "Invalid ROS interface name."
            )

        if interface_kind == "msg":
            try:
                message_type = get_message(normalized_name)
            except (
                AttributeError,
                ImportError,
                ModuleNotFoundError,
                ValueError,
            ) as exc:
                raise LookupError(
                    f"ROS message interface not found: "
                    f"{normalized_name}"
                ) from exc

            message = message_type()

            return {
                "name": normalized_name,
                "package": package_name,
                "kind": "msg",
                "interface": short_name,
                "fields": dict(
                    message.get_fields_and_field_types()
                ),
            }

        if interface_kind == "srv":
            try:
                service_type = get_service(normalized_name)
            except (
                AttributeError,
                ImportError,
                ModuleNotFoundError,
                ValueError,
            ) as exc:
                raise LookupError(
                    f"ROS service interface not found: "
                    f"{normalized_name}"
                ) from exc

            request = service_type.Request()
            response = service_type.Response()

            return {
                "name": normalized_name,
                "package": package_name,
                "kind": "srv",
                "interface": short_name,
                "request": dict(
                    request.get_fields_and_field_types()
                ),
                "response": dict(
                    response.get_fields_and_field_types()
                ),
            }

        if interface_kind == "action":
            try:
                action_type = get_action(normalized_name)
            except (
                AttributeError,
                ImportError,
                ModuleNotFoundError,
                ValueError,
            ) as exc:
                raise LookupError(
                    f"ROS action interface not found: "
                    f"{normalized_name}"
                ) from exc

            goal = action_type.Goal()
            result = action_type.Result()
            feedback = action_type.Feedback()

            return {
                "name": normalized_name,
                "package": package_name,
                "kind": "action",
                "interface": short_name,
                "goal": dict(
                    goal.get_fields_and_field_types()
                ),
                "result": dict(
                    result.get_fields_and_field_types()
                ),
                "feedback": dict(
                    feedback.get_fields_and_field_types()
                ),
            }

        raise ValueError(
            "ROS interface kind must be msg, srv, or action."
        )
