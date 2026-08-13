"""ROS 2 runtime log inspection MCP prompt."""


def inspect_runtime_logs() -> str:
    """Return a workflow for inspecting ROS 2 runtime logs."""
    return """
Inspect the ROS 2 runtime logs.

Use the available ros2_mcp tools to:

1. Read recent /rosout messages.
2. Focus on WARN, ERROR, and FATAL messages.
3. Identify nodes associated with important messages.
4. Correlate log messages with diagnostics when useful.
5. Check runtime health when the logs indicate a broader problem.

Report:

- important recent log messages
- affected nodes
- repeated warnings or errors
- likely root causes
- recommended next diagnostic steps

Do not modify the ROS 2 runtime.
""".strip()
