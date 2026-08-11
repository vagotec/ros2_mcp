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
        """Return discovered ROS services with their service types."""
        raise NotImplementedError
