"""Abstract ROS adapter interface."""

from abc import ABC, abstractmethod


class RosAdapter(ABC):
    """Define the ROS runtime operations used by the application layer."""

    @abstractmethod
    def list_nodes(self) -> list[str]:
        """Return the names of currently discovered ROS nodes."""
        raise NotImplementedError
