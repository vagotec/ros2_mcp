# Phase 3 - ROS Discovery

## Goal

Extend the read-only ROS runtime interface with graph discovery capabilities while preserving the architecture established in Phase 2.

Phase 3 adds discovery for:

* ROS nodes
* ROS topics
* ROS topic information
* ROS services

The MCP, application, and ROS adapter layers remain clearly separated.

## Scope

Phase 3 adds:

* `list_topics`
* `topic_info`
* `list_services`
* Adapter interface extensions
* ROS 2 Jazzy implementations
* RuntimeService extensions
* MCP tool registration
* Unit test extensions
* MCP integration test extensions

No topic subscription or message reading is implemented yet.

## Architecture

The architecture remains unchanged:

```text
MCP Client
    |
    v
MCP Runtime Tools
    |
    v
RuntimeService
    |
    v
RosAdapter
    |
    v
JazzyRosAdapter
    |
    v
rclpy
    |
    v
ROS 2 / DDS
```

Phase 3 extends existing interfaces instead of introducing new architectural layers.

## ROS Adapter Interface

The `RosAdapter` interface now defines:

```text
list_nodes() -> list[str]

list_topics() -> list[tuple[str, list[str]]]

topic_info(topic_name: str) -> dict[str, object]

list_services() -> list[tuple[str, list[str]]]
```

The abstract adapter remains independent from `rclpy`.

## list_nodes

`list_nodes` returns discovered ROS nodes.

The internal MCP discovery node is excluded:

```text
ros2_mcp_runtime
```

This prevents internal infrastructure from being exposed to MCP clients.

## list_topics

`list_topics` uses the ROS graph to return topic names and message types.

Example structure:

```text
[
    (
        "/cmd_vel",
        ["geometry_msgs/msg/Twist"],
    ),
    (
        "/scan",
        ["sensor_msgs/msg/LaserScan"],
    ),
]
```

ROS system topics such as:

```text
/parameter_events
/rosout
```

are intentionally not filtered.

They are legitimate ROS graph entities.

## topic_info

`topic_info` returns information about one ROS topic.

Current response fields:

```text
name
types
publisher_count
subscriber_count
```

Example:

```text
{
    "name": "/cmd_vel",
    "types": ["geometry_msgs/msg/Twist"],
    "publisher_count": 1,
    "subscriber_count": 2,
}
```

The information is obtained through ROS 2 graph APIs.

## list_services

`list_services` returns discovered service names and service types.

Example:

```text
[
    (
        "/camera/get_parameters",
        ["rcl_interfaces/srv/GetParameters"],
    )
]
```

## Internal Service Filtering

The internal `ros2_mcp_runtime` node automatically exposes ROS parameter and type-description services.

Examples include:

```text
/ros2_mcp_runtime/get_parameters
/ros2_mcp_runtime/list_parameters
/ros2_mcp_runtime/set_parameters
/ros2_mcp_runtime/get_type_description
```

These services are implementation details and are filtered from `list_services`.

This keeps MCP results focused on the external ROS system.

## Runtime Service

`RuntimeService` now exposes:

```text
list_nodes()
list_topics()
topic_info()
list_services()
```

The service continues to depend only on `RosAdapter`.

It does not import `rclpy`.

## MCP Runtime Tools

The MCP server now exposes four read-only tools:

```text
list_nodes
list_topics
topic_info
list_services
```

All tools are marked as read-only.

The MCP layer accesses ROS runtime functionality only through:

```text
AppContext
    |
    v
RuntimeService
    |
    v
RosAdapter
```

The MCP layer does not access `rclpy` directly.

## Tool Flow

Example for `topic_info`:

```text
MCP Client
    |
    v
topic_info
    |
    v
RuntimeService.topic_info()
    |
    v
RosAdapter.topic_info()
    |
    v
JazzyRosAdapter.topic_info()
    |
    v
rclpy
    |
    v
ROS Graph
```

## Read-Only Policy

All Phase 3 tools are read-only.

The project still does not allow:

* Topic publishing
* Service execution
* Parameter modification
* Actions
* Robot movement
* Lifecycle changes

## Testing

Phase 3 extends the existing test suite.

Current result:

```text
7 passed
```

Tests cover:

* MCP server creation
* RuntimeService delegation
* ROS Jazzy adapter behavior
* Internal node filtering
* Internal service filtering
* MCP tool discovery
* MCP tool execution
* Layer boundary enforcement

## Layer Boundary

Direct `rclpy` imports remain restricted to:

```text
src/ros2_mcp/ros/jazzy/
```

They are not allowed in:

```text
src/ros2_mcp/mcp/
src/ros2_mcp/application/
```

The boundary remains validated during testing.

## Files Changed

Phase 3 modifies:

```text
src/ros2_mcp/ros/adapter.py
src/ros2_mcp/ros/jazzy/adapter.py
src/ros2_mcp/application/runtime/service.py
src/ros2_mcp/mcp/runtime_tools.py
tests/unit/test_runtime_service.py
tests/integration/test_mcp_runtime_tool.py
```

## Architecture Decisions

Phase 3 confirms the following design rules:

* Existing layers are extended instead of rebuilt.
* ROS graph operations belong in the ROS adapter.
* MCP tools remain thin wrappers around application services.
* Internal MCP ROS infrastructure is hidden from external results.
* ROS system topics remain visible when they are legitimate ROS graph entities.
* Read-only behavior remains the default.

## Known Limitations

Phase 3 does not yet support reading messages from topics.

For example:

```text
/cmd_vel
/scan
/odom
/camera/image_raw
```

can be discovered, but their current messages cannot yet be read through MCP.

## Phase Status

```text
Phase 3 - ROS Discovery

COMPLETED
```

## Next Phase

Phase 4 introduces topic reading.

The primary runtime function will be:

```text
read_topic
```

Phase 4 must handle:

* Dynamic ROS message types
* Topic subscriptions
* Timeouts
* Message serialization
* Structured MCP results
* Safe cleanup of temporary subscriptions

The established MCP, application, and ROS adapter architecture will remain unchanged.

