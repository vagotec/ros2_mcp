# ROS 2 MCP

A modular MCP server for inspecting, monitoring, and later safely controlling a running ROS 2 system.

`ros2_mcp` focuses exclusively on ROS 2 runtime interaction.

ROS 2 project creation, package generation, build, and test workflows are provided separately by `ros2_dev_mcp`.

## Goals

The project provides a clean MCP interface to a running ROS 2 system.

Main goals:

- Inspect the ROS 2 graph
- Discover nodes, topics, and services
- Read ROS 2 topic data
- Inspect node endpoints
- Inspect ROS 2 parameters
- Read ROS 2 parameter values
- Inspect service endpoints
- Add controlled runtime interaction
- Keep ROS-specific implementation details behind adapters
- Keep MCP clients replaceable
- Support Codex, Claude Code, and other MCP-compatible clients

## Architecture

```text
MCP Client
    |
    v
MCP Runtime Tools
    |
    v
Runtime Service
    |
    v
ROS Adapter
    |
    v
ROS Distribution Adapter
    |
    v
rclpy
    |
    v
ROS 2 / DDS
```

Current ROS distribution:

```text
ROS 2 Jazzy
```

The MCP and application layers do not directly depend on `rclpy`.

ROS distribution-specific behavior is isolated in the ROS adapter implementation.

## Project Separation

ROS 2 runtime access and ROS 2 software development are intentionally separated.

```text
Codex / Claude Code
        |
        +--------------------+
        |                    |
        v                    v
    ros2_mcp            ros2_dev_mcp
        |                    |
        |                    |
 ROS 2 Runtime         ROS 2 Development
        |                    |
        |               create workspace
        |               create package
        |               create node
        |               create launch file
        |               build project
        |               run tests
        |
        v
 ROS 2 / DDS
```

`ros2_mcp` does not create or modify ROS 2 project files.

Developer functionality belongs to the separate `ros2_dev_mcp` project.

## Current MCP Runtime Tools

The current runtime MCP provides:

```text
list_nodes
list_topics
topic_info
list_services
read_topic
node_info
list_parameters
get_parameter
service_info
```

### `list_nodes`

Lists discovered ROS 2 nodes.

### `list_topics`

Lists discovered ROS 2 topics and their message types.

### `topic_info`

Returns information about a ROS 2 topic, including endpoint counts.

### `list_services`

Lists discovered ROS 2 services and their service types.

### `read_topic`

Reads one message from a ROS 2 topic with a configured timeout.

### `node_info`

Returns detailed graph information for a ROS 2 node.

This includes:

- publishers
- subscribers
- service servers
- service clients

### `list_parameters`

Lists parameters exposed by a ROS 2 node.

### `get_parameter`

Reads one parameter value from a ROS 2 node.

### `service_info`

Returns information about a ROS 2 service, including servers and clients.

## Project Principles

- Runtime and development tooling remain separated
- ROS access goes through a dedicated adapter
- ROS distributions should remain replaceable
- MCP clients should remain replaceable
- Runtime access starts read-only
- Write operations require explicit safety mechanisms
- Avoid private or unstable ROS APIs when possible
- No unnecessary frameworks
- No direct shell interface exposed through the runtime MCP
- Independent implementation
- External ROS MCP projects may be used for feature comparison, not code copying

## Source Structure

```text
src/ros2_mcp/
├── application/
│   └── runtime/
│       └── service.py
├── config/
│   └── settings.py
├── mcp/
│   └── runtime_tools.py
├── ros/
│   ├── adapter.py
│   └── jazzy/
│       └── adapter.py
└── server.py
```

### Application Layer

```text
src/ros2_mcp/application/runtime/
```

Contains ROS runtime use cases independent of the concrete ROS implementation.

### MCP Layer

```text
src/ros2_mcp/mcp/runtime_tools.py
```

Exposes runtime operations as MCP tools.

### ROS Adapter

```text
src/ros2_mcp/ros/adapter.py
```

Defines the ROS-independent runtime interface.

### ROS 2 Jazzy Adapter

```text
src/ros2_mcp/ros/jazzy/adapter.py
```

Implements runtime access using ROS 2 Jazzy and `rclpy`.

## Development Environment

Current development environment:

```text
Ubuntu 24.04
ROS 2 Jazzy
Python 3.12
uv
MCP Python SDK
Cyclone DDS
```

## Environment Setup

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

When using the configured ROS environment:

```bash
export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

## Install Dependencies

```bash
cd ~/projects/robotics/ros2_mcp

uv sync
source .venv/bin/activate
```

## Syntax Check

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate

python -m compileall -q src tests
```

## Runtime Tests

The remaining tests focus only on ROS runtime behavior.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q
```

Current runtime test areas:

```text
ROS Jazzy adapter
Runtime application service
MCP runtime tools
Server creation
```

## Run the MCP Server

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m ros2_mcp.server
```

The server uses the MCP standard I/O transport.

## Codex Integration

The local MCP server can be registered with Codex.

Example configuration command:

```bash
codex mcp add ros2_mcp \
  --env ROS_DOMAIN_ID=30 \
  --env RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -- \
  bash -lc 'cd /home/sarvg/projects/robotics/ros2_mcp && source /opt/ros/jazzy/setup.bash && source .venv/bin/activate && exec python -m ros2_mcp.server'
```

Check the registration:

```bash
codex mcp get ros2_mcp
```

Inside Codex:

```text
/mcp
```

The expected ROS 2 MCP tools are:

```text
get_parameter
list_nodes
list_parameters
list_services
list_topics
node_info
read_topic
service_info
topic_info
```

## Real Codex Verification

The runtime MCP was verified with Codex.

Example prompt:

```text
Use only ros2_mcp.

List the currently running ROS 2 nodes.

Do not use ros2_dev_mcp.
Do not modify files or ROS state.
```

Codex successfully called:

```text
ros2_mcp.list_nodes({})
```

This verifies the complete path:

```text
User
  |
  v
Codex
  |
  v
ros2_mcp
  |
  v
ROS Adapter
  |
  v
ROS 2 Jazzy
```

## Documentation

Historical runtime development documentation is stored in:

```text
docs/
├── README_PHASE_1.md
├── README_PHASE_2.md
├── README_PHASE_3.md
├── README_PHASE_4.md
└── README_PHASE_7.md
```

The former project-development phases were separated into the `ros2_dev_mcp` project.

## Completed Runtime Capabilities

```text
ROS graph discovery       ✅
Topic discovery           ✅
Topic information         ✅
Topic reading             ✅
Service discovery         ✅
Node information          ✅
Parameter discovery       ✅
Parameter reading         ✅
Service information       ✅
Codex MCP integration     ✅
Runtime / Dev separation  ✅
```

## Next Runtime Capabilities

The next development focus is controlled ROS 2 runtime interaction.

Planned capabilities:

```text
publish_topic
call_service
set_parameter
ROS 2 actions
process monitoring
node / launch management
logs and diagnostics
```

Write operations will require explicit safety rules.

## Future MCP Projects

The ROS MCP ecosystem is intentionally modular.

Planned separate projects include:

```text
ros2_mcp
    Generic ROS 2 runtime

ros2_dev_mcp
    ROS 2 project development

ros2_control_mcp
    ros2_control integration

moveit2_mcp
    MoveIt 2 integration

nav2_mcp
    Nav2 integration
```

Additional ROS 2 components can later receive their own MCP servers without turning `ros2_mcp` into a monolithic server.

## Repository

This project is developed independently.

Other ROS MCP implementations may be evaluated for feature and architecture comparison, but their source code is not used as a copy-and-paste implementation basis.
