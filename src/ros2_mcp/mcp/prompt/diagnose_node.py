"""ROS 2 node diagnosis MCP prompt."""


def diagnose_node(node_name: str) -> str:
    """Return a workflow for diagnosing one ROS 2 node."""
    return f"""
Diagnose the ROS 2 node:

{node_name}

Use the available ros2_mcp tools to inspect:

1. Node information.
2. Topics associated with the node.
3. Services associated with the node.
4. Actions associated with the node when present.
5. Relevant parameters when useful.
6. Diagnostics related to the node.
7. Relevant /rosout messages.
8. Runtime health when broader context is required.

Report:

- whether the node is currently discovered
- its ROS graph relationships
- suspicious interfaces
- warnings or errors
- likely runtime problems

Prefer read-only inspection.
Do not modify the node unless the user explicitly asks for a later
state-changing operation.
""".strip()
