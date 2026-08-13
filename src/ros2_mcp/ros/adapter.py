"""Abstract ROS adapter interface."""

from abc import ABC, abstractmethod


class RosAdapter(ABC):
    """Define the ROS runtime operations used by the application layer."""

    @abstractmethod
    def list_nodes(self) -> list[str]:
        """Return the names of currently discovered ROS nodes."""
        raise NotImplementedError

    @abstractmethod
    def list_topics(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS topics with their message types."""
        raise NotImplementedError

    @abstractmethod
    def topic_info(self, topic_name: str) -> dict[str, object]:
        """Return information about a ROS topic."""
        raise NotImplementedError

    @abstractmethod
    def list_services(self) -> list[tuple[str, list[str]]]:
        """Return discovered ROS services with their types."""
        raise NotImplementedError

    @abstractmethod
    def read_topic(
        self,
        topic_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Read one message from a ROS topic."""
        raise NotImplementedError

    @abstractmethod
    def node_info(self, node_name: str) -> dict[str, object]:
        """Return publishers, subscribers, services, and actions for a node."""
        raise NotImplementedError

    @abstractmethod
    def list_parameters(self, node_name: str) -> list[str]:
        """Return parameter names exposed by a ROS node."""
        raise NotImplementedError

    @abstractmethod
    def get_parameter(
        self,
        node_name: str,
        parameter_name: str,
    ) -> dict[str, object]:
        """Return one parameter value from a ROS node."""
        raise NotImplementedError

    @abstractmethod
    def service_info(self, service_name: str) -> dict[str, object]:
        """Return type, servers, and clients for a ROS service."""
        raise NotImplementedError


    @abstractmethod
    def publish_topic(
        self,
        topic_name: str,
        message_type: str,
        message: dict[str, object],
    ) -> dict[str, object]:
        """Publish one message to a ROS topic."""
        raise NotImplementedError

    @abstractmethod
    def call_service(
        self,
        service_name: str,
        service_type: str,
        request: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Call one ROS service and return its response."""
        raise NotImplementedError

    @abstractmethod
    def set_parameter(
        self,
        node_name: str,
        parameter_name: str,
        value: object,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Set one parameter on a ROS node."""
        raise NotImplementedError

    @abstractmethod
    def send_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Send one ROS action goal and wait for its result."""
        raise NotImplementedError
