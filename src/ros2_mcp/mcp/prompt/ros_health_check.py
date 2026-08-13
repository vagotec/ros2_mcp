"""ROS 2 system health-check MCP prompt."""


def ros_health_check() -> str:
    """Return a read-only workflow for evaluating ROS 2 runtime health."""
    return """
Perform a ROS 2 runtime health check.

Use the available ros2_mcp tools to:

1. List currently discovered ROS 2 nodes.
2. List currently discovered ROS 2 topics.
3. Inspect ROS 2 diagnostics.
4. Inspect recent /rosout messages.
5. Retrieve the runtime health summary.
6. Correlate warnings or errors across these sources.

Report:

- discovered runtime structure
- warnings
- errors
- diagnostic problems
- suspicious missing components
- overall runtime health

Do not modify the ROS 2 runtime.
Do not start or stop processes.
Do not publish messages or call state-changing services.
""".strip()
