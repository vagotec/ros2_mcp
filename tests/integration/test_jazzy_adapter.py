"""Integration tests for the ROS 2 Jazzy adapter."""

from ros2_mcp.ros.jazzy.adapter import JazzyRosAdapter


def test_list_nodes_hides_internal_node() -> None:
    """Verify that the internal MCP discovery node is not exposed."""
    adapter = JazzyRosAdapter()

    try:
        nodes = adapter.list_nodes()
    finally:
        adapter.close()

    assert isinstance(nodes, list)
    assert "ros2_mcp_runtime" not in nodes
