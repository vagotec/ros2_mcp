"""Register modular ROS 2 MCP prompts."""

from mcp.server import MCPServer

from ros2_mcp.mcp.prompt.diagnose_action import diagnose_action
from ros2_mcp.mcp.prompt.diagnose_node import diagnose_node
from ros2_mcp.mcp.prompt.diagnose_topic import diagnose_topic
from ros2_mcp.mcp.prompt.inspect_runtime_logs import inspect_runtime_logs
from ros2_mcp.mcp.prompt.ros_health_check import ros_health_check
from ros2_mcp.mcp.prompt.safe_runtime_review import safe_runtime_review


def register_prompts(server: MCPServer) -> None:
    """Register the generic ROS 2 workflow prompts."""

    server.prompt(
        name="ros_health_check",
        title="ROS 2 Health Check",
        description=(
            "Inspect the ROS 2 runtime and summarize its overall health."
        ),
    )(ros_health_check)

    server.prompt(
        name="diagnose_node",
        title="Diagnose ROS 2 Node",
        description=(
            "Inspect one ROS 2 node and summarize its runtime relationships "
            "and potential problems."
        ),
    )(diagnose_node)

    server.prompt(
        name="diagnose_topic",
        title="Diagnose ROS 2 Topic",
        description=(
            "Inspect one ROS 2 topic, including its type, endpoints, and QoS."
        ),
    )(diagnose_topic)

    server.prompt(
        name="diagnose_action",
        title="Diagnose ROS 2 Action",
        description=(
            "Inspect one ROS 2 action without sending or cancelling goals."
        ),
    )(diagnose_action)

    server.prompt(
        name="inspect_runtime_logs",
        title="Inspect ROS 2 Runtime Logs",
        description=(
            "Inspect ROS 2 runtime logs and correlate warnings and errors."
        ),
    )(inspect_runtime_logs)

    server.prompt(
        name="safe_runtime_review",
        title="Safe ROS 2 Runtime Review",
        description=(
            "Review ROS 2 runtime health together with active safety controls."
        ),
    )(safe_runtime_review)
