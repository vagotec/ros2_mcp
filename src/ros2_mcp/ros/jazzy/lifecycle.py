"""ROS 2 lifecycle node management."""

from lifecycle_msgs.msg import State, Transition


class LifecycleMixin:
    """Inspect and change standardized ROS lifecycle node states."""

    _TRANSITIONS = {
        "configure": Transition.TRANSITION_CONFIGURE,
        "cleanup": Transition.TRANSITION_CLEANUP,
        "activate": Transition.TRANSITION_ACTIVATE,
        "deactivate": Transition.TRANSITION_DEACTIVATE,
    }

    def get_lifecycle_state(
        self,
        node_name: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return the current lifecycle state of a ROS node."""
        normalized_node = node_name.strip()

        if not normalized_node:
            raise ValueError(
                "node_name must not be empty."
            )

        if not normalized_node.startswith("/"):
            normalized_node = f"/{normalized_node}"

        response = self.call_service(
            service_name=f"{normalized_node}/get_state",
            service_type="lifecycle_msgs/srv/GetState",
            request={},
            timeout_sec=timeout_sec,
        )

        state = response["response"]["current_state"]

        return {
            "node": normalized_node,
            "state": state,
        }

    def change_lifecycle_state(
        self,
        node_name: str,
        transition: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Request a standardized lifecycle transition."""
        normalized_node = node_name.strip()

        if not normalized_node:
            raise ValueError(
                "node_name must not be empty."
            )

        if not normalized_node.startswith("/"):
            normalized_node = f"/{normalized_node}"

        normalized_transition = transition.strip().lower()

        transition_id = self._TRANSITIONS.get(
            normalized_transition
        )

        if normalized_transition == "shutdown":
            state_result = self.get_lifecycle_state(
                normalized_node,
                timeout_sec,
            )

            state_id = state_result["state"]["id"]

            if isinstance(state_id, (bytes, bytearray)):
                state_id = state_id[0]

            if state_id == State.PRIMARY_STATE_UNCONFIGURED:
                transition_id = (
                    Transition.TRANSITION_UNCONFIGURED_SHUTDOWN
                )
            elif state_id == State.PRIMARY_STATE_INACTIVE:
                transition_id = (
                    Transition.TRANSITION_INACTIVE_SHUTDOWN
                )
            elif state_id == State.PRIMARY_STATE_ACTIVE:
                transition_id = (
                    Transition.TRANSITION_ACTIVE_SHUTDOWN
                )
            else:
                raise ValueError(
                    "Shutdown is not valid from the current lifecycle state."
                )

        if transition_id is None:
            raise ValueError(
                "transition must be configure, cleanup, "
                "activate, deactivate, or shutdown."
            )

        response = self.call_service(
            service_name=f"{normalized_node}/change_state",
            service_type="lifecycle_msgs/srv/ChangeState",
            request={
                "transition": {
                    "id": transition_id,
                    "label": "",
                }
            },
            timeout_sec=timeout_sec,
        )

        return {
            "node": normalized_node,
            "transition": normalized_transition,
            "transition_id": transition_id,
            "response": response["response"],
        }
