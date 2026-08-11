# Phase 4 - Topic Reading

## Goal

Add read-only topic message access to the ROS 2 MCP server without changing the established modular architecture.

Phase 4 introduces:

```text
read_topic
```

The implementation dynamically discovers the ROS message type, creates a temporary subscription, waits for one message within a configurable timeout, converts the message to a structured representation, and then removes the subscription again.

## Scope

Phase 4 contains:

* `read_topic` in `RosAdapter`
* `read_topic` in `JazzyRosAdapter`
* Dynamic ROS message type loading
* Temporary ROS subscriptions
* Dedicated executor usage
* Message serialization
* Configurable read timeout
* RuntimeService integration
* MCP tool integration
* Unit test extension
* MCP integration test extension

No topic publishing is introduced.

## Architecture

The architecture remains unchanged:

```text
MCP Client
    |
    v
read_topic
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
ROS 2 Topic
```

## Adapter Interface

The `RosAdapter` interface now includes:

```text
read_topic(
    topic_name: str,
    timeout_sec: float,
) -> dict[str, object]
```

The abstract adapter remains independent from `rclpy`.

## Dynamic Message Types

The Jazzy adapter discovers the message type from the ROS graph.

Example:

```text
/odom
    ->
nav_msgs/msg/Odometry
```

The corresponding Python message class is loaded dynamically through:

```text
rosidl_runtime_py.utilities.get_message
```

This means `read_topic` does not need hard-coded imports for message types such as:

```text
std_msgs/msg/String
geometry_msgs/msg/Twist
sensor_msgs/msg/LaserScan
nav_msgs/msg/Odometry
```

## Temporary Subscription

For every `read_topic` call, the adapter:

```text
discover topic type
    |
    v
create subscription
    |
    v
wait for one message
    |
    v
destroy subscription
```

The subscription is not stored permanently.

This supports the stateless design goal of the MCP server.

## ROS Executor

The ROS adapter uses its own:

```text
Context
Node
SingleThreadedExecutor
```

All three belong to the same isolated ROS context.

This avoids using the global rclpy executor and prevents context mismatches.

The executor is created during adapter initialization and destroyed during adapter shutdown.

## Timeout Behavior

`read_topic` does not wait indefinitely.

The timeout is loaded from:

```text
config/ros2_mcp.toml
```

Current configuration:

```toml
[runtime]
read_topic_timeout_sec = 1.0
```

The MCP tool uses this value automatically.

The timeout is therefore configurable without modifying application code.

## Timeout Result

If no message is received before the timeout expires, the result contains:

```text
message: None
```

Example:

```text
{
    "topic": "/odom",
    "type": "nav_msgs/msg/Odometry",
    "message": None,
}
```

A timeout is treated as a normal runtime condition rather than an exception.

## Unknown Topic

If the requested topic cannot be discovered, the current result is:

```text
{
    "topic": "/unknown_topic",
    "type": None,
    "message": None,
}
```

## Message Serialization

ROS message objects are converted into structured Python data using:

```text
rosidl_runtime_py.convert.message_to_ordereddict
```

This allows MCP clients to receive structured message data instead of ROS-specific Python objects.

Example:

```text
{
    "topic": "/chatter",
    "type": "std_msgs/msg/String",
    "message": {
        "data": "hello"
    }
}
```

## Runtime Service

`RuntimeService` now exposes:

```text
read_topic(
    topic_name,
    timeout_sec,
)
```

The service delegates the operation to `RosAdapter`.

It does not import `rclpy`.

## MCP Tool

The MCP server now exposes:

```text
read_topic
```

The MCP client only provides:

```text
topic_name
```

The timeout comes from application configuration.

Example MCP request:

```text
read_topic(
    topic_name="/odom"
)
```

The tool remains read-only.

## Current Runtime Tools

The MCP server now provides:

```text
list_nodes
list_topics
topic_info
list_services
read_topic
```

All current runtime tools are read-only.

## Configuration

Phase 4 introduces the first external configuration file:

```text
config/ros2_mcp.toml
```

Configuration loading is implemented in:

```text
src/ros2_mcp/config/settings.py
```

Current configuration structure:

```text
Settings
    |
    v
RuntimeSettings
    |
    v
read_topic_timeout_sec
```

Values that can vary between environments should be placed in configuration rather than unnecessarily hard-coded.

## MCP Lifecycle

Settings are loaded during MCP server startup.

The application lifecycle now creates:

```text
Settings
JazzyRosAdapter
RuntimeService
```

These resources are stored in:

```text
AppContext
```

The MCP tools access them through the server lifespan context.

## Read-Only Policy

Phase 4 remains fully read-only.

The server still does not support:

* Topic publishing
* Service calls
* Parameter modification
* Action execution
* Lifecycle changes
* Robot movement

## Testing

Current result:

```text
8 passed
```

Tests cover:

* MCP server creation
* RuntimeService delegation
* ROS adapter discovery
* ROS service filtering
* `read_topic` application delegation
* MCP tool registration
* MCP `read_topic` execution
* Layer boundary enforcement

## Layer Boundary

Direct `rclpy` imports remain restricted to:

```text
src/ros2_mcp/ros/jazzy/
```

They remain forbidden in:

```text
src/ros2_mcp/mcp/
src/ros2_mcp/application/
```

## Files Added

Phase 4 adds:

```text
config/ros2_mcp.toml
src/ros2_mcp/config/settings.py
```

## Files Modified

Phase 4 modifies:

```text
src/ros2_mcp/ros/adapter.py
src/ros2_mcp/ros/jazzy/adapter.py
src/ros2_mcp/application/runtime/service.py
src/ros2_mcp/mcp/runtime_tools.py
src/ros2_mcp/server.py
tests/unit/test_runtime_service.py
tests/integration/test_mcp_runtime_tool.py
```

## Architecture Decisions

Phase 4 establishes the following design rules:

* Dynamic ROS message types are resolved at runtime.
* Topic subscriptions are temporary.
* ROS subscriptions are owned by the ROS adapter.
* MCP does not manage ROS subscriptions directly.
* ROS execution uses an adapter-owned executor.
* Timeouts are configuration values.
* Topic read timeout is not considered an error.
* ROS messages are converted before crossing the adapter boundary.
* No permanent topic subscriber state is stored.

## Known Limitations

The current implementation reads only one message per request.

It does not yet support:

```text
continuous streaming
multiple messages
message history
QoS selection
large message limits
binary payload optimization
```

These can be evaluated later if required.

## Phase Status

```text
Phase 4 - Topic Reading

COMPLETED
```

## Next Phase

Phase 5 introduces the Project Adapter.

Planned functionality includes:

```text
create_workspace
create_package
create_node
create_launch_file
create_parameter_file
create_tests
```

Project filesystem access must remain restricted to approved project roots.

The initial allowed root will be based on the configured project security boundary.
