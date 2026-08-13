"""ROS 2 Jazzy parameters runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class ParametersMixin:
    """Provide ROS 2 Jazzy parameters operations."""

    def list_parameters(self, node_name: str) -> list[str]:
        """Return parameter names exposed by a discovered ROS node."""
        from rcl_interfaces.srv import ListParameters

        base_name, namespace = self._normalize_node_name(node_name)

        if not self._wait_for_node(
            base_name=base_name,
            namespace=namespace,
            timeout_sec=1.0,
        ):
            raise LookupError(f"ROS node not found: {node_name}")

        service_name = f"{namespace.rstrip('/')}/{base_name}/list_parameters"
        client = self._node.create_client(
            ListParameters,
            service_name,
        )

        try:
            if not client.wait_for_service(timeout_sec=1.0):
                raise LookupError(
                    f"Parameter service not available: {service_name}"
                )

            request = ListParameters.Request()
            request.depth = 0

            future = client.call_async(request)

            self._spin_until_future_complete(
                future,
                timeout_sec=1.0,
            )

            if not future.done():
                raise TimeoutError(
                    f"Timed out listing parameters for {node_name}"
                )

            response = future.result()

            if response is None:
                raise RuntimeError(
                    f"Parameter request failed for {node_name}"
                )

            return sorted(response.result.names)
        finally:
            self._node.destroy_client(client)

    def get_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> dict[str, object]:
        """Return one parameter value from a discovered ROS node."""
        from rcl_interfaces.msg import ParameterType
        from rcl_interfaces.srv import GetParameters

        base_name, namespace = self._normalize_node_name(node_name)

        if not self._wait_for_node(
            base_name=base_name,
            namespace=namespace,
            timeout_sec=1.0,
        ):
            raise LookupError(f"ROS node not found: {node_name}")

        service_name = f"{namespace.rstrip('/')}/{base_name}/get_parameters"
        client = self._node.create_client(
            GetParameters,
            service_name,
        )

        try:
            if not client.wait_for_service(timeout_sec=1.0):
                raise LookupError(
                    f"Parameter service not available: {service_name}"
                )

            request = GetParameters.Request()
            request.names = [parameter_name]

            future = client.call_async(request)

            self._spin_until_future_complete(
                future,
                timeout_sec=1.0,
            )

            if not future.done():
                raise TimeoutError(
                    f"Timed out reading parameter {parameter_name}"
                )

            response = future.result()

            if response is None or not response.values:
                raise RuntimeError(
                    f"Parameter request failed: {parameter_name}"
                )

            value = response.values[0]

            type_map = {
                ParameterType.PARAMETER_NOT_SET: ("not_set", None),
                ParameterType.PARAMETER_BOOL: (
                    "bool",
                    value.bool_value,
                ),
                ParameterType.PARAMETER_INTEGER: (
                    "integer",
                    value.integer_value,
                ),
                ParameterType.PARAMETER_DOUBLE: (
                    "double",
                    value.double_value,
                ),
                ParameterType.PARAMETER_STRING: (
                    "string",
                    value.string_value,
                ),
                ParameterType.PARAMETER_BYTE_ARRAY: (
                    "byte_array",
                    list(value.byte_array_value),
                ),
                ParameterType.PARAMETER_BOOL_ARRAY: (
                    "bool_array",
                    list(value.bool_array_value),
                ),
                ParameterType.PARAMETER_INTEGER_ARRAY: (
                    "integer_array",
                    list(value.integer_array_value),
                ),
                ParameterType.PARAMETER_DOUBLE_ARRAY: (
                    "double_array",
                    list(value.double_array_value),
                ),
                ParameterType.PARAMETER_STRING_ARRAY: (
                    "string_array",
                    list(value.string_array_value),
                ),
            }

            parameter_type, parameter_value = type_map.get(
                value.type,
                ("unknown", None),
            )

            return {
                "node": node_name,
                "parameter": parameter_name,
                "type": parameter_type,
                "value": parameter_value,
            }
        finally:
            self._node.destroy_client(client)

    def set_parameter(
        self,
        node_name: str,
        parameter_name: str,
        value: object,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Set one parameter on a discovered ROS node."""
        # # SAFETY:JazzyRosAdapter:set_parameter
        self._validate_parameter_write(node_name, parameter_name)
        from rcl_interfaces.srv import SetParameters
        from rclpy.parameter import Parameter

        normalized_parameter = parameter_name.strip()

        if not normalized_parameter:
            raise ValueError("Parameter name must not be empty.")

        if timeout_sec <= 0:
            raise ValueError("Parameter timeout must be greater than zero.")

        base_name, namespace = self._normalize_node_name(node_name)

        if not self._wait_for_node(
            base_name=base_name,
            namespace=namespace,
            timeout_sec=timeout_sec,
        ):
            raise LookupError(f"ROS node not found: {node_name}")

        service_name = (
            f"{namespace.rstrip('/')}/{base_name}/set_parameters"
        )

        client = self._node.create_client(
            SetParameters,
            service_name,
        )

        try:
            if not client.wait_for_service(timeout_sec=timeout_sec):
                raise LookupError(
                    f"Parameter service not available: {service_name}"
                )

            try:
                parameter = Parameter(
                    normalized_parameter,
                    value=value,
                )
                parameter_message = parameter.to_parameter_msg()
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid ROS parameter value for "
                    f"{normalized_parameter}: {exc}"
                ) from exc

            request = SetParameters.Request()
            request.parameters = [parameter_message]

            future = client.call_async(request)

            self._spin_until_future_complete(
                future,
                timeout_sec=timeout_sec,
            )

            if not future.done():
                raise TimeoutError(
                    f"Timed out setting parameter "
                    f"{normalized_parameter} on {node_name}"
                )

            response = future.result()

            if response is None or not response.results:
                raise RuntimeError(
                    f"Parameter update failed: {normalized_parameter}"
                )

            result = response.results[0]

            return {
                "node": node_name,
                "parameter": normalized_parameter,
                "value": value,
                "successful": result.successful,
                "reason": result.reason,
            }
        finally:
            self._node.destroy_client(client)
