"""ROS 2 topic diagnosis MCP prompt."""


def diagnose_topic(topic_name: str) -> str:
    """Return a workflow for diagnosing one ROS 2 topic."""
    return f"""
Diagnose the ROS 2 topic:

{topic_name}

Use the available ros2_mcp tools to inspect:

1. Topic information.
2. Message interface type.
3. Publishers and subscribers.
4. Endpoint QoS settings.
5. Recommended compatible QoS when useful.
6. Recent topic messages when appropriate.
7. Related nodes when broader context is useful.

Report:

- whether the topic exists
- message type
- publisher/subscriber relationships
- QoS compatibility issues
- suspicious or missing data
- likely causes of communication problems

Do not publish to the topic.
Perform read-only diagnosis.
""".strip()
