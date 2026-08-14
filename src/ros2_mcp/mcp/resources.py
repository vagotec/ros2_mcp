"""Register modular ROS 2 MCP resources."""

from mcp.server import MCPServer

from ros2_mcp.mcp.resource.action_info import (
    register_action_info_resource,
)
from ros2_mcp.mcp.resource.actions import register_actions_resource
from ros2_mcp.mcp.resource.node_info import register_node_info_resource
from ros2_mcp.mcp.resource.nodes import register_nodes_resource
from ros2_mcp.mcp.resource.runtime_health import (
    register_runtime_health_resource,
)
from ros2_mcp.mcp.resource.safety_guardrails import (
    register_safety_guardrails_resource,
)
from ros2_mcp.mcp.resource.services import register_services_resource
from ros2_mcp.mcp.resource.topic_info import register_topic_info_resource
from ros2_mcp.mcp.resource.topics import register_topics_resource


def register_resources(server: MCPServer) -> None:
    """Register read-only ROS 2 MCP resources."""
    register_runtime_health_resource(server)
    register_safety_guardrails_resource(server)

    register_nodes_resource(server)
    register_topics_resource(server)
    register_services_resource(server)
    register_actions_resource(server)

    register_node_info_resource(server)
    register_topic_info_resource(server)
    register_action_info_resource(server)
