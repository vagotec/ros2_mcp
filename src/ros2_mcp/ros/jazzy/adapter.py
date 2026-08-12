"""ROS 2 Jazzy adapter implementation."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message

from ros2_mcp.ros.adapter import RosAdapter


class JazzyRosAdapter(RosAdapter):
    """Provide ROS runtime access through ROS 2 Jazzy and rclpy."""

    _NODE_NAME = "ros2_mcp_runtime"

    def __init__(self) -> None:
        """Initialize an isolated ROS context, node, and executor."""
        self._context = Context()
        rclpy.init(context=self._context)

        self._node = Node(
            self._NODE_NAME,
            context=self._context,
        )

        self._executor = SingleThreadedExecutor(
            context=self._context,
        )
        self._executor.add_node(self._node)

    def list_nodes(self) -> list[str]:
        """Return discovered ROS nodes excluding the internal MCP node."""
        nodes = self._node.get_node_names()

        return sorted(
            node_name
            for node_name in nodes
            if node_name != self._NODE_NAME
        )

    def list_topics(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS topics with their message types."""
        topics = self._node.get_topic_names_and_types()

        return sorted(
            (topic_name, sorted(topic_types))
            for topic_name, topic_types in topics
        )

    def topic_info(self, topic_name: str) -> dict[str, object]:
        """Return types and endpoint counts for a ROS topic."""
        topics = dict(self._node.get_topic_names_and_types())

        return {
            "name": topic_name,
            "types": sorted(topics.get(topic_name, [])),
            "publisher_count": self._node.count_publishers(topic_name),
            "subscriber_count": self._node.count_subscribers(topic_name),
        }

    def list_services(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS services excluding internal MCP services."""
        services = self._node.get_service_names_and_types()
        internal_prefix = f"/{self._NODE_NAME}/"

        return sorted(
            (service_name, sorted(service_types))
            for service_name, service_types in services
            if not service_name.startswith(internal_prefix)
        )

    def read_topic(
        self,
        topic_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read one message from a ROS topic within a timeout."""
        topics = dict(self._node.get_topic_names_and_types())
        topic_types = topics.get(topic_name, [])

        if not topic_types:
            return {
                "topic": topic_name,
                "type": None,
                "message": None,
            }

        message_type_name = topic_types[0]
        message_type = get_message(message_type_name)
        received_message = None

        def callback(message: object) -> None:
            nonlocal received_message
            received_message = message

        subscription = self._node.create_subscription(
            message_type,
            topic_name,
            callback,
            10,
        )

        try:
            self._executor.spin_once(
                timeout_sec=timeout_sec,
            )
        finally:
            self._node.destroy_subscription(subscription)

        return {
            "topic": topic_name,
            "type": message_type_name,
            "message": (
                message_to_ordereddict(received_message)
                if received_message is not None
                else None
            ),
        }

    def close(self) -> None:
        """Destroy ROS resources owned by this adapter."""
        self._executor.remove_node(self._node)
        self._executor.shutdown()
        self._node.destroy_node()
        rclpy.shutdown(context=self._context)

    def node_info(self, node_name: str) -> dict[str, object]:
        """Return runtime graph information for a discovered ROS node."""
        base_name, namespace = self._normalize_node_name(node_name)

        if not self._wait_for_node(
            base_name=base_name,
            namespace=namespace,
            timeout_sec=1.0,
        ):
            raise LookupError(f"ROS node not found: {node_name}")

        publishers = self._node.get_publisher_names_and_types_by_node(
            base_name,
            namespace,
        )
        subscribers = self._node.get_subscriber_names_and_types_by_node(
            base_name,
            namespace,
        )
        service_servers = self._node.get_service_names_and_types_by_node(
            base_name,
            namespace,
        )
        service_clients = self._node.get_client_names_and_types_by_node(
            base_name,
            namespace,
        )

        return {
            "node": node_name,
            "publishers": [
                {"name": name, "types": types}
                for name, types in sorted(publishers)
            ],
            "subscribers": [
                {"name": name, "types": types}
                for name, types in sorted(subscribers)
            ],
            "service_servers": [
                {"name": name, "types": types}
                for name, types in sorted(service_servers)
            ],
            "service_clients": [
                {"name": name, "types": types}
                for name, types in sorted(service_clients)
            ],
        }

    def _normalize_node_name(self, node_name: str) -> tuple[str, str]:
        """Split a fully qualified ROS node name into name and namespace."""
        normalized_name = node_name.strip()

        if not normalized_name:
            raise ValueError("Node name must not be empty.")

        normalized_name = normalized_name.lstrip("/")

        if "/" not in normalized_name:
            return normalized_name, "/"

        namespace, base_name = normalized_name.rsplit("/", 1)

        if not base_name:
            raise ValueError(f"Invalid ROS node name: {node_name}")

        return base_name, f"/{namespace}"

    def _wait_for_node(
        self,
        base_name: str,
        namespace: str,
        timeout_sec: float,
    ) -> bool:
        """Wait briefly until a ROS node appears in the local graph."""
        import time

        deadline = time.monotonic() + timeout_sec
        expected = (base_name, namespace)

        while time.monotonic() < deadline:
            if expected in self._node.get_node_names_and_namespaces():
                return True

            remaining = deadline - time.monotonic()

            self._executor.spin_once(
                timeout_sec=min(0.1, max(0.0, remaining))
            )

        return expected in self._node.get_node_names_and_namespaces()

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

            self._executor.spin_until_future_complete(
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

            self._executor.spin_until_future_complete(
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

    def service_info(self, service_name: str) -> dict[str, object]:
        """Return type, servers, and clients for a discovered ROS service."""
        normalized_service = service_name.strip()

        if not normalized_service:
            raise ValueError("Service name must not be empty.")

        if not normalized_service.startswith("/"):
            normalized_service = f"/{normalized_service}"

        # Give ROS discovery a short opportunity to update the local graph.
        self._executor.spin_once(timeout_sec=0.2)

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


    def publish_topic(
        self,
        topic_name: str,
        message_type: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Publish one dynamically typed message to a ROS topic."""
        from rosidl_runtime_py.set_message import set_message_fields

        normalized_topic = topic_name.strip()
        normalized_type = message_type.strip()

        if not normalized_topic:
            raise ValueError("Topic name must not be empty.")

        if not normalized_topic.startswith("/"):
            normalized_topic = f"/{normalized_topic}"

        if not normalized_type:
            raise ValueError("Message type must not be empty.")

        if not isinstance(message, dict):
            raise TypeError("Message must be a dictionary.")

        try:
            ros_message_type = get_message(normalized_type)
        except (AttributeError, ImportError, ModuleNotFoundError, ValueError) as exc:
            raise ValueError(
                f"Unknown ROS message type: {normalized_type}"
            ) from exc

        ros_message = ros_message_type()

        try:
            set_message_fields(
                ros_message,
                message,
            )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid message for ROS type {normalized_type}: {exc}"
            ) from exc

        publisher = self._node.create_publisher(
            ros_message_type,
            normalized_topic,
            10,
        )

        try:
            # Give DDS a short opportunity to discover existing subscribers.
            self._executor.spin_once(timeout_sec=0.2)

            subscriber_count = self._node.count_subscribers(
                normalized_topic
            )

            publisher.publish(ros_message)

            # Allow the middleware to process the outgoing publication.
            self._executor.spin_once(timeout_sec=0.1)

            return {
                "topic": normalized_topic,
                "type": normalized_type,
                "message": message_to_ordereddict(ros_message),
                "subscriber_count": subscriber_count,
                "published": True,
            }
        finally:
            self._node.destroy_publisher(publisher)
