"""ROS 2 Jazzy actions runtime operations."""

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message
from ros2_mcp.ros.adapter import RosAdapter


class ActionsMixin:
    """Provide ROS 2 Jazzy actions operations."""

    def send_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Send one dynamically typed ROS action goal and wait for its result."""
        # # SAFETY:JazzyRosAdapter:send_action_goal
        self._validate_action_write(action_name)
        from rclpy.action import ActionClient
        from rosidl_runtime_py.set_message import set_message_fields
        from rosidl_runtime_py.utilities import get_action

        normalized_action = action_name.strip()
        normalized_type = action_type.strip()

        if not normalized_action:
            raise ValueError("Action name must not be empty.")

        if not normalized_action.startswith("/"):
            normalized_action = f"/{normalized_action}"

        if not normalized_type:
            raise ValueError("Action type must not be empty.")

        if not isinstance(goal, dict):
            raise TypeError("Action goal must be a dictionary.")

        if timeout_sec <= 0:
            raise ValueError("Action timeout must be greater than zero.")

        try:
            ros_action_type = get_action(normalized_type)
        except (
            AttributeError,
            ImportError,
            ModuleNotFoundError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"Unknown ROS action type: {normalized_type}"
            ) from exc

        ros_goal = ros_action_type.Goal()

        try:
            set_message_fields(
                ros_goal,
                goal,
            )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid goal for ROS action type "
                f"{normalized_type}: {exc}"
            ) from exc

        feedback_messages: list[dict[str, object]] = []

        def feedback_callback(feedback_message: object) -> None:
            """Collect structured ROS action feedback."""
            feedback_messages.append(
                message_to_ordereddict(feedback_message.feedback)
            )

        action_client = ActionClient(
            self._node,
            ros_action_type,
            normalized_action,
        )

        try:
            if not action_client.wait_for_server(
                timeout_sec=timeout_sec
            ):
                raise LookupError(
                    f"ROS action server not available: "
                    f"{normalized_action}"
                )

            goal_future = action_client.send_goal_async(
                ros_goal,
                feedback_callback=feedback_callback,
            )

            self._spin_until_future_complete(
                goal_future,
                timeout_sec=timeout_sec,
            )

            if not goal_future.done():
                raise TimeoutError(
                    f"Timed out sending ROS action goal: "
                    f"{normalized_action}"
                )

            goal_handle = goal_future.result()

            if goal_handle is None:
                raise RuntimeError(
                    f"ROS action goal failed: {normalized_action}"
                )

            if not goal_handle.accepted:
                return {
                    "action": normalized_action,
                    "type": normalized_type,
                    "goal": message_to_ordereddict(ros_goal),
                    "accepted": False,
                    "status": None,
                    "result": None,
                    "feedback": feedback_messages,
                    "completed": False,
                }

            result_future = goal_handle.get_result_async()

            self._spin_until_future_complete(
                result_future,
                timeout_sec=timeout_sec,
            )

            if not result_future.done():
                raise TimeoutError(
                    f"Timed out waiting for ROS action result: "
                    f"{normalized_action}"
                )

            result_response = result_future.result()

            if result_response is None:
                raise RuntimeError(
                    f"ROS action returned no result: "
                    f"{normalized_action}"
                )

            return {
                "action": normalized_action,
                "type": normalized_type,
                "goal": message_to_ordereddict(ros_goal),
                "accepted": True,
                "status": result_response.status,
                "result": message_to_ordereddict(
                    result_response.result
                ),
                "feedback": feedback_messages,
                "completed": True,
            }
        finally:
            destroy = getattr(action_client, "destroy", None)

            if callable(destroy):
                destroy()

    @staticmethod
    def _ros_integer(value: object) -> int:
        """Convert ROS integer-like values to Python int."""
        if isinstance(value, (bytes, bytearray)):
            if len(value) != 1:
                raise ValueError(
                    "Expected exactly one byte for ROS integer value."
                )

            return value[0]

        return int(value)

    @staticmethod
    def _goal_id_string(goal_handle: object) -> str:
        """Convert a ROS action goal UUID to a stable hexadecimal string."""
        goal_id = goal_handle.goal_id
        raw_uuid = getattr(goal_id, "uuid", goal_id)

        try:
            uuid_bytes = bytes(raw_uuid)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Unable to convert ROS action goal UUID."
            ) from exc

        if len(uuid_bytes) != 16:
            raise ValueError(
                f"ROS action goal UUID must contain 16 bytes, "
                f"got {len(uuid_bytes)}."
            )

        return uuid_bytes.hex()

    @staticmethod
    def _action_status_name(status: int) -> str:
        """Return a readable ROS action goal status."""
        from action_msgs.msg import GoalStatus

        names = {
            GoalStatus.STATUS_UNKNOWN: "UNKNOWN",
            GoalStatus.STATUS_ACCEPTED: "ACCEPTED",
            GoalStatus.STATUS_EXECUTING: "EXECUTING",
            GoalStatus.STATUS_CANCELING: "CANCELING",
            GoalStatus.STATUS_SUCCEEDED: "SUCCEEDED",
            GoalStatus.STATUS_CANCELED: "CANCELED",
            GoalStatus.STATUS_ABORTED: "ABORTED",
        }

        return names.get(status, f"UNKNOWN_{status}")

    def _refresh_action_goal(
        self,
        entry: dict[str, object],
        timeout_sec: float,
    ) -> None:
        """Process ROS events and refresh one managed action goal."""
        import time

        result_future = entry["result_future"]

        if entry.get("completed"):
            return

        deadline = time.monotonic() + timeout_sec

        while time.monotonic() < deadline:
            if result_future.done():
                break

            remaining = deadline - time.monotonic()

            if remaining <= 0:
                break

            self._spin_once(
                timeout_sec=min(0.05, remaining),
            )

        if not result_future.done():
            goal_handle = entry["goal_handle"]
            status = self._ros_integer(goal_handle.status)

            entry["status"] = status
            return

        result_response = result_future.result()

        if result_response is None:
            entry["completed"] = True
            entry["status"] = None
            entry["result"] = None
            return

        status = self._ros_integer(result_response.status)

        entry["completed"] = True
        entry["status"] = status
        entry["result"] = message_to_ordereddict(
            result_response.result
        )

        action_client = entry.get("action_client")

        if action_client is not None:
            destroy = getattr(action_client, "destroy", None)

            if callable(destroy):
                destroy()

            entry["action_client"] = None

    def _action_goal_result(
        self,
        goal_id: str,
        entry: dict[str, object],
    ) -> dict[str, object]:
        """Return one managed action goal as structured MCP data."""
        status = entry.get("status")

        return {
            "goal_id": goal_id,
            "action": entry["action"],
            "type": entry["type"],
            "goal": entry["goal"],
            "accepted": True,
            "status": status,
            "status_name": (
                self._action_status_name(status)
                if status is not None
                else None
            ),
            "completed": bool(entry.get("completed")),
            "result": entry.get("result"),
            "feedback": list(entry["feedback"]),
        }

    def start_action_goal(
        self,
        action_name: str,
        action_type: str,
        goal: dict[str, object],
        timeout_sec: float,
    ) -> dict[str, object]:
        """Start a ROS action goal and retain its lifecycle state."""
        # # SAFETY:JazzyRosAdapter:start_action_goal
        self._validate_action_write(action_name)
        from rclpy.action import ActionClient
        from rosidl_runtime_py.set_message import set_message_fields
        from rosidl_runtime_py.utilities import get_action

        normalized_action = action_name.strip()
        normalized_type = action_type.strip()

        if not normalized_action:
            raise ValueError("Action name must not be empty.")

        if not normalized_action.startswith("/"):
            normalized_action = f"/{normalized_action}"

        if not normalized_type:
            raise ValueError("Action type must not be empty.")

        if not isinstance(goal, dict):
            raise TypeError("Action goal must be a dictionary.")

        if timeout_sec <= 0:
            raise ValueError("Action timeout must be greater than zero.")

        try:
            ros_action_type = get_action(normalized_type)
        except (
            AttributeError,
            ImportError,
            ModuleNotFoundError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"Unknown ROS action type: {normalized_type}"
            ) from exc

        ros_goal = ros_action_type.Goal()

        try:
            set_message_fields(
                ros_goal,
                goal,
            )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid goal for ROS action type "
                f"{normalized_type}: {exc}"
            ) from exc

        feedback_messages: list[dict[str, object]] = []

        def feedback_callback(feedback_message: object) -> None:
            """Collect structured ROS action feedback."""
            feedback_messages.append(
                message_to_ordereddict(feedback_message.feedback)
            )

        action_client = ActionClient(
            self._node,
            ros_action_type,
            normalized_action,
        )

        if not action_client.wait_for_server(
            timeout_sec=timeout_sec
        ):
            action_client.destroy()

            raise LookupError(
                f"ROS action server not available: "
                f"{normalized_action}"
            )

        goal_future = action_client.send_goal_async(
            ros_goal,
            feedback_callback=feedback_callback,
        )

        self._spin_until_future_complete(
            goal_future,
            timeout_sec=timeout_sec,
        )

        if not goal_future.done():
            action_client.destroy()

            raise TimeoutError(
                f"Timed out sending ROS action goal: "
                f"{normalized_action}"
            )

        goal_handle = goal_future.result()

        if goal_handle is None:
            action_client.destroy()

            raise RuntimeError(
                f"ROS action goal failed: {normalized_action}"
            )

        if not goal_handle.accepted:
            action_client.destroy()

            return {
                "goal_id": None,
                "action": normalized_action,
                "type": normalized_type,
                "goal": message_to_ordereddict(ros_goal),
                "accepted": False,
                "status": None,
                "status_name": None,
                "completed": False,
                "result": None,
                "feedback": feedback_messages,
            }

        goal_id = self._goal_id_string(goal_handle)
        result_future = goal_handle.get_result_async()
        status = self._ros_integer(goal_handle.status)

        self._active_action_goals[goal_id] = {
            "action": normalized_action,
            "type": normalized_type,
            "goal": message_to_ordereddict(ros_goal),
            "goal_handle": goal_handle,
            "result_future": result_future,
            "action_client": action_client,
            "feedback": feedback_messages,
            "status": status,
            "completed": False,
            "result": None,
        }

        return self._action_goal_result(
            goal_id,
            self._active_action_goals[goal_id],
        )

    def get_action_status(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Return and refresh the state of a managed action goal."""
        normalized_goal_id = goal_id.strip().lower()

        if not normalized_goal_id:
            raise ValueError("goal_id must not be empty.")

        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be greater than zero.")

        entry = self._active_action_goals.get(
            normalized_goal_id
        )

        if entry is None:
            raise LookupError(
                f"Managed ROS action goal not found: "
                f"{normalized_goal_id}"
            )

        self._refresh_action_goal(
            entry,
            timeout_sec,
        )

        return self._action_goal_result(
            normalized_goal_id,
            entry,
        )

    def cancel_action_goal(
        self,
        goal_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Request cancellation of a managed ROS action goal."""
        normalized_goal_id = goal_id.strip().lower()

        if not normalized_goal_id:
            raise ValueError("goal_id must not be empty.")

        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be greater than zero.")

        entry = self._active_action_goals.get(
            normalized_goal_id
        )

        if entry is None:
            raise LookupError(
                f"Managed ROS action goal not found: "
                f"{normalized_goal_id}"
            )

        self._refresh_action_goal(
            entry,
            min(timeout_sec, 0.05),
        )

        if entry.get("completed"):
            result = self._action_goal_result(
                normalized_goal_id,
                entry,
            )
            result["cancel_requested"] = False
            result["cancel_accepted"] = False
            result["cancel_return_code"] = None
            result["reason"] = "Goal already completed."

            return result

        goal_handle = entry["goal_handle"]

        cancel_future = goal_handle.cancel_goal_async()

        self._spin_until_future_complete(
            cancel_future,
            timeout_sec=timeout_sec,
        )

        if not cancel_future.done():
            raise TimeoutError(
                f"Timed out canceling ROS action goal: "
                f"{normalized_goal_id}"
            )

        cancel_response = cancel_future.result()

        if cancel_response is None:
            raise RuntimeError(
                f"ROS action cancel returned no response: "
                f"{normalized_goal_id}"
            )

        return_code = self._ros_integer(
            cancel_response.return_code
        )

        goals_canceling = list(
            cancel_response.goals_canceling
        )

        cancel_accepted = bool(goals_canceling)

        entry["status"] = self._ros_integer(
            goal_handle.status
        )

        result = self._action_goal_result(
            normalized_goal_id,
            entry,
        )

        result["cancel_requested"] = True
        result["cancel_accepted"] = cancel_accepted
        result["cancel_return_code"] = return_code
        result["goals_canceling"] = len(
            goals_canceling
        )

        return result

    @staticmethod
    def _action_type_from_transport_type(
        transport_type: str,
    ) -> str | None:
        """Convert a generated action transport type to its action type."""
        suffixes = (
            "_FeedbackMessage",
            "_SendGoal",
            "_GetResult",
        )

        for suffix in suffixes:
            if transport_type.endswith(suffix):
                action_type = transport_type[
                    :-len(suffix)
                ]

                if "/action/" in action_type:
                    return action_type

        return None

    def list_actions(
        self,
    ) -> list[tuple[str, list[str]]]:
        """Discover ROS actions from standardized action transport endpoints."""
        discovered: dict[str, set[str]] = {}

        feedback_suffix = "/_action/feedback"

        for topic_name, topic_types in (
            self._node.get_topic_names_and_types()
        ):
            if not topic_name.endswith(
                feedback_suffix
            ):
                continue

            action_name = topic_name[
                :-len(feedback_suffix)
            ]

            action_types = discovered.setdefault(
                action_name,
                set(),
            )

            for transport_type in topic_types:
                action_type = (
                    self._action_type_from_transport_type(
                        transport_type
                    )
                )

                if action_type is not None:
                    action_types.add(
                        action_type
                    )

        service_suffixes = (
            "/_action/send_goal",
            "/_action/get_result",
        )

        for service_name, service_types in (
            self._node.get_service_names_and_types()
        ):
            matched_suffix = next(
                (
                    suffix
                    for suffix in service_suffixes
                    if service_name.endswith(suffix)
                ),
                None,
            )

            if matched_suffix is None:
                continue

            action_name = service_name[
                :-len(matched_suffix)
            ]

            action_types = discovered.setdefault(
                action_name,
                set(),
            )

            for transport_type in service_types:
                action_type = (
                    self._action_type_from_transport_type(
                        transport_type
                    )
                )

                if action_type is not None:
                    action_types.add(
                        action_type
                    )

        return sorted(
            (
                action_name,
                sorted(action_types),
            )
            for action_name, action_types
            in discovered.items()
        )

    @staticmethod
    def _node_fqn(
        node_name: str,
        namespace: str,
    ) -> str:
        """Build one fully qualified ROS node name."""
        normalized_namespace = namespace.rstrip("/")

        if not normalized_namespace:
            normalized_namespace = ""

        return (
            f"{normalized_namespace}/"
            f"{node_name.lstrip('/')}"
        )

    def action_info(
        self,
        action_name: str,
    ) -> dict[str, object]:
        """Return types, servers, clients, and transport endpoints."""
        normalized_action = action_name.strip()

        if not normalized_action:
            raise ValueError(
                "Action name must not be empty."
            )

        if not normalized_action.startswith("/"):
            normalized_action = (
                f"/{normalized_action}"
            )

        actions = dict(
            self.list_actions()
        )

        action_types = actions.get(
            normalized_action,
            [],
        )

        if not action_types:
            raise LookupError(
                f"ROS action not found: "
                f"{normalized_action}"
            )

        send_goal_service = (
            f"{normalized_action}"
            "/_action/send_goal"
        )

        servers: set[str] = set()
        clients: set[str] = set()

        for node_name, namespace in (
            self._node.get_node_names_and_namespaces()
        ):
            node_fqn = self._node_fqn(
                node_name,
                namespace,
            )

            try:
                service_servers = (
                    self._node
                    .get_service_names_and_types_by_node(
                        node_name,
                        namespace,
                    )
                )
            except Exception:
                service_servers = []

            if any(
                name == send_goal_service
                for name, _ in service_servers
            ):
                servers.add(node_fqn)

            try:
                service_clients = (
                    self._node
                    .get_client_names_and_types_by_node(
                        node_name,
                        namespace,
                    )
                )
            except Exception:
                service_clients = []

            if any(
                name == send_goal_service
                for name, _ in service_clients
            ):
                clients.add(node_fqn)

        return {
            "name": normalized_action,
            "types": sorted(action_types),
            "server_count": len(servers),
            "client_count": len(clients),
            "servers": sorted(servers),
            "clients": sorted(clients),
            "transport": {
                "send_goal_service": (
                    f"{normalized_action}"
                    "/_action/send_goal"
                ),
                "get_result_service": (
                    f"{normalized_action}"
                    "/_action/get_result"
                ),
                "cancel_goal_service": (
                    f"{normalized_action}"
                    "/_action/cancel_goal"
                ),
                "feedback_topic": (
                    f"{normalized_action}"
                    "/_action/feedback"
                ),
                "status_topic": (
                    f"{normalized_action}"
                    "/_action/status"
                ),
            },
        }
