"""Safe ROS 2 runtime review MCP prompt."""


def safe_runtime_review() -> str:
    """Return a workflow for reviewing runtime state and safety controls."""
    return """
Perform a safe review of the current ROS 2 runtime.

Use the available ros2_mcp tools to inspect:

1. Runtime health.
2. Active safety guardrails.
3. Currently discovered nodes.
4. Relevant diagnostics.
5. Recent warning, error, or fatal /rosout messages.
6. Managed ROS processes, launches, and rosbag operations when useful.

Report:

- current runtime health
- active safety restrictions
- protected resources
- configured runtime limits
- managed resources
- warnings or errors
- operations that should require dry-run validation

Do not change the ROS 2 runtime.
Do not start or stop resources.
Do not attempt to bypass safety guardrails.
""".strip()
