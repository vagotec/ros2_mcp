# Phase 2 - ROS Adapter

## Goal

Introduce the ROS runtime abstraction and connect the MCP server to ROS 2 Jazzy through a dedicated adapter.

The goal of this phase is to keep ROS-specific code isolated from the MCP and application layers.

## Scope

Phase 2 contains:

* ROS adapter abstraction
* ROS 2 Jazzy adapter implementation
* rclpy integration
* ROS runtime application service
* First read-only runtime operation: `list_nodes`
* MCP tool registration for `list_nodes`
* MCP lifecycle integration
* Unit tests
* ROS integration tests
* MCP integration test

No topic, service, parameter, action, publishing, or project-management functionality is added in this phase.

## Architecture

```text
MCP Client
    |
    v
MCP Tool
list_nodes
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

## Module Structure

```text
src/ros2_mcp/
├── application/
│   └── runtime/
│       └── service.py
├── mcp/
│   └── runtime_tools.py
├── ros/
│   ├── adapter.py
│   └── jazzy/
│       └── adapter.py
└── server.py
```

## ROS Adapter

`RosAdapter` defines the ROS operations required by the application layer.

Current interface:

```text
list_nodes() -> list[str]
```

The abstract adapter does not import or depend directly on `rclpy`.

This allows future ROS distribution implementations to replace the Jazzy implementation without changing the application or MCP layers.

## Jazzy ROS Adapter

`JazzyRosAdapter` implements `RosAdapter` using ROS 2 Jazzy and `rclpy`.

Responsibilities:

* Create an isolated ROS context
* Create an internal ROS discovery node
* Query the ROS graph
* Return discovered node names
* Hide the internal MCP discovery node
* Destroy ROS resources cleanly during shutdown

The internal ROS node name is:

```text
ros2_mcp_runtime
```

This internal node is filtered from results returned to MCP clients.

## Python and ROS Environment

The project uses:

```text
Python project dependencies
    -> uv
    -> .venv

ROS 2 Python runtime
    -> system ROS 2 Jazzy installation
    -> /opt/ros/jazzy
```

The virtual environment is created with access to system site packages.

This allows the project to use the official ROS 2 Jazzy Python packages while keeping project-specific Python dependencies managed by uv.

`rclpy` is not installed through uv.

Current ROS environment:

```text
ROS_DISTRO=jazzy
ROS_VERSION=2
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

## Runtime Service

`RuntimeService` represents the application layer.

It depends only on the `RosAdapter` abstraction.

It does not import `rclpy` and does not know which ROS distribution is being used.

Current operation:

```text
RuntimeService.list_nodes()
```

The service delegates the operation to:

```text
RosAdapter.list_nodes()
```

## MCP Runtime Tool

Phase 2 introduces the first ROS MCP tool:

```text
list_nodes
```

The tool is read-only.

Its execution path is:

```text
MCP Client
    |
    v
list_nodes
    |
    v
RuntimeService.list_nodes()
    |
    v
RosAdapter.list_nodes()
    |
    v
JazzyRosAdapter
    |
    v
rclpy
```

The MCP layer does not import `rclpy`.

## MCP Lifecycle

ROS resources are created through the MCP server lifespan.

Startup:

```text
MCP server starts
    |
    v
JazzyRosAdapter created
    |
    v
RuntimeService created
    |
    v
AppContext created
```

Runtime:

```text
MCP Tool
    |
    v
AppContext
    |
    v
RuntimeService
    |
    v
JazzyRosAdapter
```

Shutdown:

```text
MCP server stops
    |
    v
JazzyRosAdapter.close()
    |
    v
ROS node destroyed
    |
    v
ROS context shutdown
```

This prevents ROS resources from being created and destroyed for every MCP request.

## Read-Only Policy

The current MCP runtime interface is intentionally read-only.

Phase 2 does not allow:

* Topic publishing
* Service calls
* Action execution
* Parameter modification
* Lifecycle changes
* Robot movement
* File modification

The `list_nodes` MCP tool is marked as read-only.

## Layer Boundary

Direct `rclpy` imports are restricted to the ROS adapter implementation.

Allowed:

```text
src/ros2_mcp/ros/jazzy/
```

Not allowed:

```text
src/ros2_mcp/mcp/
src/ros2_mcp/application/
```

This boundary is explicitly validated during testing.

## Tests

Phase 2 contains four passing tests.

### Server Unit Test

Verifies that the MCP server factory returns an `MCPServer`.

### Runtime Service Unit Test

Uses a fake `RosAdapter`.

This verifies the application layer independently from ROS 2.

### Jazzy Adapter Integration Test

Creates the real `JazzyRosAdapter` and verifies that:

* ROS resources can be initialized
* Node discovery returns a list
* The internal `ros2_mcp_runtime` node is hidden
* Resources are closed cleanly

### MCP Integration Test

Uses the MCP SDK in-memory client.

It verifies the complete chain:

```text
MCP Client
    |
    v
list_nodes
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
```

Current result:

```text
4 passed
```

## Files Added or Changed

```text
src/ros2_mcp/ros/adapter.py
src/ros2_mcp/ros/jazzy/adapter.py
src/ros2_mcp/application/runtime/service.py
src/ros2_mcp/mcp/runtime_tools.py
src/ros2_mcp/server.py
tests/unit/test_runtime_service.py
tests/integration/test_jazzy_adapter.py
tests/integration/test_mcp_runtime_tool.py
```

## Architecture Decisions

Phase 2 establishes the following permanent design decisions:

* MCP must not access `rclpy` directly.
* The application layer must depend on `RosAdapter`.
* ROS distribution-specific behavior belongs in dedicated adapter implementations.
* ROS resources use a controlled lifecycle.
* Internal infrastructure nodes are not exposed as user ROS nodes.
* ROS runtime operations start read-only.
* Unit tests should work without requiring an active ROS graph.
* Integration tests may use the real ROS environment.
* MCP integration should be tested through the official MCP client API.

## Known Limitations

Phase 2 supports only:

```text
list_nodes
```

It does not yet support:

* Topic discovery
* Topic information
* Service discovery
* Topic reading
* Parameters
* Services
* Actions
* TF
* Lifecycle
* Publishing
* Multi-robot operation

## Phase Status

```text
Phase 2 - ROS Adapter

COMPLETED
```

## Next Phase

Phase 3 introduces ROS graph discovery:

```text
list_topics
topic_info
list_services
```

These operations will extend the existing adapter, application service, and MCP runtime tool modules without changing the established architecture.
