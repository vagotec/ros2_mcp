"""ROS 2 action diagnosis MCP prompt."""


def diagnose_action(action_name: str) -> str:
    """Return a workflow for diagnosing one ROS 2 action."""
    return f"""
Diagnose the ROS 2 action:

{action_name}

Use the available ros2_mcp tools to inspect:

1. Action information.
2. Action interface type.
3. Action servers and clients when visible.
4. Related nodes.
5. Relevant diagnostics.
6. Relevant /rosout messages.
7. Current action status information when available.

Report:

- whether the action exists
- its interface
- discovered runtime relationships
- warnings or errors
- likely action communication problems

Do not send a goal.
Do not cancel a goal.
Perform read-only diagnosis.
""".strip()
