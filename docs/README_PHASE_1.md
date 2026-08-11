# Phase 1 - Foundation

## Goal

Create a minimal, modular, and testable foundation for the ROS 2 MCP project without adding ROS runtime functionality yet.

## Scope

Phase 1 contains:

* Git repository initialization
* uv project initialization
* Python 3.12 environment
* Modular package structure
* MCP Python SDK dependency
* pytest development dependency
* Minimal MCP server factory
* CLI entry point
* Unit test configuration
* First unit test

ROS runtime access is intentionally not implemented in this phase.

## Architecture Established

```text
src/ros2_mcp/
├── application/
│   ├── project/
│   └── runtime/
├── config/
├── mcp/
├── project/
│   └── filesystem/
├── ros/
│   └── jazzy/
├── __init__.py
└── server.py
```

## Module Responsibilities

### `mcp/`

MCP protocol integration and MCP tools.

### `application/`

Application services and use cases.

### `ros/`

ROS abstraction and ROS-distribution-specific adapters.

### `project/`

Project and filesystem adapter implementations.

### `config/`

Configuration loading and validation.

### `server.py`

MCP server creation and process entry point.

## Dependencies

Runtime:

* Python >= 3.12 and < 3.13
* MCP Python SDK >= 2 and < 3

Development:

* pytest >= 9.1.1

The exact resolved dependency versions are stored in `uv.lock`.

## MCP Server

The current server contains only the MCP server factory and stdio entry point.

No ROS tools are registered yet.

## Testing

pytest plugin auto-loading is disabled for this project.

This prevents unrelated ROS 2 pytest plugins from being loaded automatically from the system ROS installation during isolated unit tests.

Current test:

```text
tests/unit/test_server.py
```

The test verifies that the server factory returns an `MCPServer` instance.

## CLI

The project exposes the console entry point:

```text
ros2-mcp
```

It maps to:

```text
ros2_mcp.server:main
```

## Configuration Rule

Values that may vary between systems or deployments must not be unnecessarily hard-coded.

When configuration becomes necessary, configurable values will be loaded through the dedicated `config` module from configuration files.

Examples include:

* Allowed project root
* ROS distribution
* Timeouts
* Limits
* Transport settings
* Write-safety settings

## Security Boundary

The project workspace is:

```text
~/projects/robotics/ros2_mcp
```

Project-management functionality added in later phases must restrict filesystem access to explicitly allowed roots.

No system-wide modifications are part of Phase 1.

## Validation

Phase 1 validation includes:

* Python environment check
* MCP import check
* MCP server factory check
* Python syntax check
* pytest execution
* uv lock consistency check
* CLI entry point check

## Known Limitations

Phase 1 intentionally does not include:

* rclpy integration
* ROS graph discovery
* Topic access
* Project generation
* Service calls
* Actions
* Publishing
* Docker
* Kubernetes

These capabilities belong to later phases.

## Next Phase

Phase 2 introduces:

* ROS adapter abstraction
* ROS 2 Jazzy adapter
* rclpy integration
* First read-only runtime function: `list_nodes`
