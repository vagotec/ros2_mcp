# ROS 2 MCP

A modular MCP server for inspecting, monitoring, and controlled interaction with a running ROS 2 system.

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
- Publish structured ROS 2 messages
- Call ROS 2 services
- Modify ROS 2 parameters
- Send ROS 2 Action goals
- Receive ROS 2 Action results and feedback
- Keep ROS-specific implementation details behind adapters
- Keep ROS distributions replaceable
- Keep MCP clients replaceable
- Support Codex and other MCP-compatible clients
- Keep runtime and development responsibilities separated
- Avoid exposing arbitrary shell execution through the runtime MCP

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

This allows future ROS distribution adapters to be introduced without coupling the MCP protocol layer to a specific ROS 2 distribution.

## Project Separation

ROS 2 runtime access and ROS 2 software development are intentionally separated.

```text
Codex / MCP Client
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
        |               create parameter file
        |               create tests
        |               build project
        |               run tests
        |
        v
 ROS 2 / DDS
```

`ros2_mcp` does not create or modify ROS 2 project files.

Developer functionality belongs to the separate `ros2_dev_mcp` project.

The separation prevents runtime interaction and software-development functionality from becoming coupled inside one MCP server.

## Runtime Interaction Model

The runtime MCP provides two categories of operations.

### Read-Only Runtime Inspection

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

These tools inspect the running ROS 2 system.

### Controlled Runtime Interaction

```text
publish_topic
call_service
set_parameter
send_action_goal
```

These operations can change or influence the state of a running ROS 2 system.

They are therefore exposed as explicit MCP operations instead of arbitrary shell or ROS CLI execution.

The interaction architecture is:

```text
MCP Client
    |
    v
Explicit MCP Tool
    |
    v
Structured Input
    |
    v
Runtime Service
    |
    v
ROS Adapter
    |
    v
Controlled ROS 2 Operation
```

## Current MCP Runtime Tools

The current runtime MCP provides 13 tools:

```text
call_service
get_parameter
list_nodes
list_parameters
list_services
list_topics
node_info
publish_topic
read_topic
send_action_goal
service_info
set_parameter
topic_info
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

### `publish_topic`

Publishes one structured message to a ROS 2 topic.

Example:

```text
Topic:
/chatter

Type:
std_msgs/msg/String
```

Structured message:

```json
{
  "data": "hello from ros2_mcp"
}
```

The message type is resolved dynamically by the ROS 2 Jazzy adapter.

### `call_service`

Calls a ROS 2 service using structured request data.

Example:

```text
Service:
/mcp_test/set_enabled

Type:
std_srvs/srv/SetBool
```

Request:

```json
{
  "data": true
}
```

The service type is dynamically resolved by the ROS adapter.

### `set_parameter`

Changes a parameter exposed by a running ROS 2 node.

Example:

```text
Node:
/mcp_parameter_test

Parameter:
enabled

Value:
true
```

The operation returns the success state and any ROS-provided reason.

### `send_action_goal`

Sends a goal to a ROS 2 Action server and waits for the result.

Example:

```text
Action:
/mcp_test/fibonacci

Type:
example_interfaces/action/Fibonacci
```

Goal:

```json
{
  "order": 8
}
```

The runtime adapter supports:

```text
goal submission
goal acceptance
feedback
result
status
```

The action type is resolved dynamically.

## Project Principles

- Runtime and development tooling remain separated
- ROS access goes through a dedicated adapter
- ROS distributions should remain replaceable
- MCP clients should remain replaceable
- Read and write operations remain clearly distinguishable
- Runtime write operations are exposed explicitly
- Avoid private or unstable ROS APIs when possible
- No unnecessary frameworks
- No arbitrary shell interface exposed through the runtime MCP
- No arbitrary ROS CLI execution exposed through the runtime MCP
- Independent implementation
- External ROS MCP projects may be used for feature and architecture comparison, not code copying
- Generic ROS functionality remains separate from subsystem-specific MCP servers

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

The MCP layer does not directly access `rclpy`.

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

ROS-specific functionality remains isolated inside this layer.

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

The test suite focuses on the ROS runtime architecture.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q
```

Current verified result:

```text
8 passed
```

Current runtime test areas include:

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
call_service
get_parameter
list_nodes
list_parameters
list_services
list_topics
node_info
publish_topic
read_topic
send_action_goal
service_info
set_parameter
topic_info
```

Expected tool count:

```text
13
```

## Real Codex Verification

The runtime MCP has been verified with Codex against a real ROS 2 Jazzy environment.

The tests intentionally instructed Codex to:

```text
Use only ros2_mcp.
Do not use shell commands.
Do not modify files.
Do not use ros2_dev_mcp.
```

This verifies that Codex can use the MCP runtime interface directly instead of falling back to shell commands.

### Runtime Inspection

Example:

```text
Use only ros2_mcp.

List the currently running ROS 2 nodes.

Do not use ros2_dev_mcp.
Do not modify files or ROS state.
```

Codex successfully selected:

```text
ros2_mcp.list_nodes
```

### Topic Publishing

Codex was instructed to publish:

```text
hello from codex
```

to:

```text
/chatter
```

using:

```text
std_msgs/msg/String
```

Codex selected:

```text
ros2_mcp.publish_topic
```

An independent ROS 2 subscriber received:

```text
data: hello from codex
---
```

### Service Call

A real ROS 2 service was available at:

```text
/mcp_test/set_enabled
```

using:

```text
std_srvs/srv/SetBool
```

Codex called:

```text
ros2_mcp.call_service
```

with:

```json
{
  "data": true
}
```

The returned response was:

```json
{
  "success": true,
  "message": "enabled"
}
```

The ROS 2 service server independently logged the request.

### Parameter Write

A real ROS 2 node exposed:

```text
/mcp_parameter_test
```

with parameter:

```text
enabled
```

Codex selected:

```text
ros2_mcp.set_parameter
```

and changed the value to:

```text
true
```

Independent ROS 2 verification returned:

```text
Boolean value is: True
```

### ROS 2 Action

A real ActionServer was available at:

```text
/mcp_test/fibonacci
```

using:

```text
example_interfaces/action/Fibonacci
```

Codex selected:

```text
ros2_mcp.send_action_goal
```

with:

```json
{
  "order": 8
}
```

The goal was accepted and completed.

Result:

```json
{
  "sequence": [
    0,
    1,
    1,
    2,
    3,
    5,
    8,
    13
  ]
}
```

The ActionServer independently confirmed execution.

## Verified Runtime Path

The complete runtime path has therefore been tested:

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
MCP Runtime Tool
  |
  v
Runtime Service
  |
  v
ROS Adapter
  |
  v
ROS 2 Jazzy Adapter
  |
  v
rclpy
  |
  v
ROS 2 / DDS
```

This has been verified for:

```text
graph inspection
topic publishing
service calls
parameter writes
action goals
```

## Documentation

Runtime development documentation is stored in:

```text
docs/
├── README_PHASE_1.md
├── README_PHASE_2.md
├── README_PHASE_3.md
├── README_PHASE_4.md
├── README_PHASE_5.md
└── README_PHASE_6.md
```

The former project-development functionality was separated into the dedicated:

```text
ros2_dev_mcp
```

project.

Phase 5 documents extended runtime inspection.

Phase 6 documents controlled ROS 2 runtime interaction.

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

Topic publishing          ✅
Service calls             ✅
Parameter writing         ✅
ROS 2 Action goals        ✅
Action feedback           ✅
Action results            ✅

Codex MCP integration     ✅
Runtime / Dev separation  ✅
Real ROS 2 verification   ✅
```

## Verified MCP Tool Inventory

The server was queried directly after the Phase 6 implementation.

Result:

```text
Tool count: 13
Missing expected tools: none
```

Registered tools:

```text
call_service
get_parameter
list_nodes
list_parameters
list_services
list_topics
node_info
publish_topic
read_topic
send_action_goal
service_info
set_parameter
topic_info
```

## Controlled Interaction Safety

The runtime MCP can now modify the state of a running ROS 2 system.

The following operations are therefore write operations:

```text
publish_topic
call_service
set_parameter
send_action_goal
```

These operations can have real effects.

For example:

```text
geometry_msgs/msg/Twist
```

published to a robot velocity topic could cause robot motion.

A service call could enable hardware.

A parameter change could alter controller behavior.

An Action goal could initiate a longer-running robot operation.

For this reason, generic runtime interaction remains separated from future subsystem-specific control servers.

The project does not expose arbitrary shell commands as a substitute for explicit MCP tools.

## Current Limitations

The current implementation intentionally remains focused.

Not currently implemented:

```text
persistent publisher registry
continuous publishing
MCP-configurable QoS
action cancellation
long-running action sessions
process start/stop
launch management
generic shell execution
generic ROS CLI execution
robot-specific safety policies
```

These capabilities are not required for the current generic runtime foundation.

## Next Runtime Capabilities

The core ROS 2 runtime interaction mechanisms are now implemented.

Future generic runtime improvements may include:

```text
logs
diagnostics
process monitoring
additional runtime health information
optional QoS controls
additional safety policies
```

Process and launch management should only be added if they clearly belong to the runtime MCP and can be exposed safely without turning the project into a generic shell interface.

## Future MCP Projects

The ROS MCP ecosystem is intentionally modular.

Planned separate projects include:

```text
ros2_mcp
    Generic ROS 2 runtime inspection and interaction

ros2_dev_mcp
    ROS 2 project development

ros2_control_mcp
    ros2_control integration

moveit2_mcp
    MoveIt 2 integration

nav2_mcp
    Nav2 integration
```

The generic runtime MCP provides foundational ROS 2 primitives.

Specialized MCP servers can later provide higher-level subsystem semantics and additional safety policies.

For example:

```text
ros2_control_mcp
    controller management
    hardware interfaces
    controller states
    resource management

moveit2_mcp
    planning
    robot state
    motion execution
    planning scenes

nav2_mcp
    navigation goals
    maps
    localization
    navigation state
```

This avoids turning `ros2_mcp` into a monolithic robotics server.

## Current Project Status

The generic runtime foundation is operational.

```text
Phase 1   Runtime foundation                 ✅
Phase 2   ROS graph discovery                ✅
Phase 3   Topic runtime inspection           ✅
Phase 4   Runtime architecture expansion     ✅
Phase 5   Extended runtime inspection        ✅
Phase 6   Controlled runtime interaction     ✅
```

Phase 6 provides the four fundamental ROS 2 interaction mechanisms:

```text
Topic       publish_topic
Service     call_service
Parameter   set_parameter
Action      send_action_goal
```

All four have been tested against a real ROS 2 Jazzy runtime.

All four have also been exercised through Codex using `ros2_mcp`.

## Repository

This project is developed independently.

Other ROS MCP implementations may be evaluated for feature and architecture comparison, but their source code is not used as a copy-and-paste implementation basis.

The architecture and implementation of `ros2_mcp` are developed specifically for this project.

