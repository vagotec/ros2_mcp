"""ROS 2 Jazzy services runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class ServicesMixin:
    """Provide ROS 2 Jazzy services operations."""

    def service_info(self, service_name: str) -> dict[str, object]:
        """Return type, servers, and clients for a discovered ROS service."""
        normalized_service = service_name.strip()

        if not normalized_service:
            raise ValueError("Service name must not be empty.")

        if not normalized_service.startswith("/"):
            normalized_service = f"/{normalized_service}"

        # Give ROS discovery a short opportunity to update the local graph.
        self._spin_once(timeout_sec=0.2)

        discovered_services = dict(self._node.get_service_names_and_types())

        if normalized_service not in discovered_services:
            raise LookupError(
                f"ROS service not found: {normalized_service}"
            )

        servers: list[str] = []
        clients: list[str] = []

        for node_name, namespace in self._node.get_node_names_and_namespaces():
            if node_name == self._NODE_NAME and namespace == "/":
                continue

            full_node_name = (
                f"/{node_name}"
                if namespace == "/"
                else f"{namespace.rstrip('/')}/{node_name}"
            )

            node_services = self._node.get_service_names_and_types_by_node(
                node_name,
                namespace,
            )

            if any(
                name == normalized_service
                for name, _ in node_services
            ):
                servers.append(full_node_name)

            node_clients = self._node.get_client_names_and_types_by_node(
                node_name,
                namespace,
            )

            if any(
                name == normalized_service
                for name, _ in node_clients
            ):
                clients.append(full_node_name)

        return {
            "service": normalized_service,
            "types": discovered_services[normalized_service],
            "servers": sorted(servers),
            "clients": sorted(clients),
        }

    def call_service(
        self,
        service_name: str,
        service_type: str,
        request: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Call one dynamically typed ROS service."""
        # # SAFETY:JazzyRosAdapter:call_service
        self._validate_service_write(service_name)
        from rosidl_runtime_py.convert import message_to_ordereddict
        from rosidl_runtime_py.set_message import set_message_fields
        from rosidl_runtime_py.utilities import get_service

        normalized_service = service_name.strip()
        normalized_type = service_type.strip()

        if not normalized_service:
            raise ValueError("Service name must not be empty.")

        if not normalized_service.startswith("/"):
            normalized_service = f"/{normalized_service}"

        if not normalized_type:
            raise ValueError("Service type must not be empty.")

        if not isinstance(request, dict):
            raise TypeError("Service request must be a dictionary.")

        if timeout_sec <= 0:
            raise ValueError("Service timeout must be greater than zero.")

        try:
            ros_service_type = get_service(normalized_type)
        except (AttributeError, ImportError, ModuleNotFoundError, ValueError) as exc:
            raise ValueError(
                f"Unknown ROS service type: {normalized_type}"
            ) from exc

        ros_request = ros_service_type.Request()

        try:
            set_message_fields(
                ros_request,
                request,
            )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid request for ROS service type {normalized_type}: {exc}"
            ) from exc

        client = self._node.create_client(
            ros_service_type,
            normalized_service,
        )

        try:
            if not client.wait_for_service(timeout_sec=timeout_sec):
                raise LookupError(
                    f"ROS service not available: {normalized_service}"
                )

            future = client.call_async(ros_request)

            self._spin_until_future_complete(
                future,
                timeout_sec=timeout_sec,
            )

            if not future.done():
                raise TimeoutError(
                    f"Timed out calling ROS service: {normalized_service}"
                )

            response = future.result()

            if response is None:
                raise RuntimeError(
                    f"ROS service call failed: {normalized_service}"
                )

            return {
                "service": normalized_service,
                "type": normalized_type,
                "request": message_to_ordereddict(ros_request),
                "response": message_to_ordereddict(response),
                "completed": True,
            }
        finally:
            self._node.destroy_client(client)
