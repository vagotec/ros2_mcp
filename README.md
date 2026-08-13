# ROS 2 MCP

A modular MCP server for inspecting, monitoring, and safely interacting with a running ROS 2 system.

`ros2_mcp` focuses exclusively on ROS 2 runtime interaction.

ROS 2 project creation, package generation, build, and test workflows are provided separately by:

```text
ros2_dev_mcp
```

The project currently targets:

```text
ROS 2 Jazzy
Ubuntu 24.04
Python 3.12
rclpy
MCP Python SDK
```

The current implementation exposes:

```text
46 MCP runtime tools
```

and has been verified through:

```text
Python syntax checks
unit and regression tests
real ROS 2 Jazzy integration tests
direct MCP client tests
Codex end-to-end tests
```

---

# Goals

The project provides a clean MCP interface to a running ROS 2 system.

Main goals:

- Inspect the ROS 2 graph
- Discover nodes, topics, services, actions, parameters, and interfaces
- Read ROS 2 topic data
- Read multiple topic messages
- Inspect topic QoS
- Automatically recommend compatible QoS
- Publish structured ROS 2 messages
- Maintain persistent publishers
- Call ROS 2 services
- Read and modify ROS 2 parameters
- Discover and inspect ROS 2 Actions
- Send ROS 2 Action goals
- Receive ROS 2 Action feedback and results
- Manage long-running Action goals
- Cancel Action goals
- Read `/rosout`
- Read ROS diagnostics
- Generate a runtime health summary
- Start and stop managed ROS processes
- Start and stop managed ROS launch files
- Inspect and change lifecycle node states
- Record and play rosbag2 data
- Keep ROS-specific implementation details behind adapters
- Keep ROS distributions replaceable
- Keep MCP clients replaceable
- Support Codex and other MCP-compatible clients
- Keep runtime and development responsibilities separated
- Avoid exposing arbitrary shell execution
- Avoid exposing arbitrary ROS CLI execution
- Apply configurable runtime safety guardrails
- Keep subsystem-specific behavior outside the generic runtime MCP

---

# Project Boundary

`ros2_mcp` is responsible for interacting with a running ROS 2 system.

Its responsibilities include:

```text
runtime inspection
runtime monitoring
runtime diagnostics
controlled runtime interaction
runtime process management
runtime launch management
ROS lifecycle operations
rosbag2 operations
QoS inspection
runtime safety
```

It does not create or modify ROS 2 software projects.

Development functionality belongs to:

```text
ros2_dev_mcp
```

Examples include:

```text
create workspace
create package
create node
create launch file
create parameter file
create tests
build project
run tests
```

The separation is intentional.

```text
Codex / MCP Client
        |
        +-------------------------+
        |                         |
        v                         v
    ros2_mcp                 ros2_dev_mcp
        |                         |
        v                         v
 ROS 2 Runtime             ROS 2 Development
```

This prevents runtime operations and filesystem/software-development operations from becoming coupled inside one MCP server.

---

# Architecture

The runtime architecture is layered.

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
rclpy / ROS 2 Runtime APIs
    |
    v
ROS 2 / DDS
```

Current ROS distribution:

```text
ROS 2 Jazzy
```

The MCP and application layers do not directly depend on `rclpy`.

ROS distribution-specific behavior is isolated behind the ROS adapter layer.

This allows future ROS distribution adapters to be introduced without changing the MCP protocol-facing API.

---

# Runtime Layer Responsibilities

## MCP Layer

```text
src/ros2_mcp/mcp/runtime_tools.py
```

Responsibilities:

```text
MCP tool definitions
structured MCP input
structured MCP output
tool annotations
delegation to RuntimeService
```

The MCP layer does not directly use `rclpy`.

---

## Application Layer

```text
src/ros2_mcp/application/runtime/service.py
```

Responsibilities:

```text
runtime use cases
delegation through RosAdapter
ROS-independent application logic
```

---

## RosAdapter

```text
src/ros2_mcp/ros/adapter.py
```

Defines the abstract runtime contract.

The application layer depends on this abstraction instead of depending on the concrete Jazzy implementation.

---

## ROS 2 Jazzy Adapter

```text
src/ros2_mcp/ros/jazzy/
```

Contains the concrete ROS 2 Jazzy implementation.

The implementation uses focused modules instead of one large monolithic adapter.

---

# Modular ROS 2 Jazzy Architecture

The original Jazzy adapter grew to more than 2,000 lines during runtime feature development.

It was therefore decomposed into dedicated modules.

Current structure:

```text
src/ros2_mcp/ros/jazzy/
├── actions.py
├── adapter.py
├── diagnostics.py
├── graph.py
├── __init__.py
├── interfaces.py
├── launches.py
├── lifecycle.py
├── logging.py
├── parameters.py
├── processes.py
├── publishers.py
├── qos.py
├── qos_auto.py
├── rosbag.py
├── safety.py
├── services.py
└── topics.py
```

The main:

```text
adapter.py
```

is now primarily responsible for:

```text
ROS context initialization
runtime node creation
executor creation
executor synchronization
shared registries
mixin composition
cleanup
```

ROS functionality lives in dedicated modules.

---

# Jazzy Adapter Composition

The concrete adapter composes the runtime features through mixins.

Conceptually:

```text
JazzyRosAdapter
    |
    +--> GraphMixin
    +--> TopicsMixin
    +--> ServicesMixin
    +--> ParametersMixin
    +--> ActionsMixin
    +--> LoggingMixin
    +--> DiagnosticsMixin
    +--> InterfacesMixin
    +--> QoSMixin
    +--> PublishersMixin
    +--> ProcessMixin
    +--> LaunchMixin
    +--> LifecycleMixin
    +--> RosbagMixin
    +--> AutoQoSMixin
    +--> SafetyMixin
    |
    +--> RosAdapter
```

The complete abstract adapter contract has been verified.

Expected result:

```text
Abstract methods: []
```

---

# Runtime Interaction Model

The runtime MCP exposes explicit operations instead of arbitrary shell execution.

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
RuntimeService
    |
    v
RosAdapter
    |
    v
Controlled ROS 2 Operation
```

The server does not expose:

```text
arbitrary shell
arbitrary ros2 CLI
arbitrary Python execution
filesystem development operations
```

This keeps runtime capabilities individually:

```text
testable
documentable
restrictable
observable
```

---

# Current MCP Runtime Tools

The final generic ROS 2 runtime MCP provides:

```text
46 tools
```

Current inventory:

```text
action_info
call_service
cancel_action_goal
change_lifecycle_state
create_persistent_publisher
destroy_persistent_publisher
get_action_status
get_bag_info
get_diagnostics
get_lifecycle_state
get_parameter
get_ros_launch
get_ros_process
get_runtime_health
get_safety_guardrails
get_topic_qos
interface_info
list_actions
list_interfaces
list_nodes
list_parameters
list_persistent_publishers
list_ros_launches
list_ros_processes
list_services
list_topics
node_info
publish_topic
publish_with_publisher
read_rosout
read_topic
read_topic_messages
recommend_topic_qos
send_action_goal
service_info
set_parameter
start_action_goal
start_bag_playback
start_bag_recording
start_ros_launch
start_ros_process
stop_bag_playback
stop_bag_recording
stop_ros_launch
stop_ros_process
topic_info
```

---

# Runtime Capability Groups

## Graph and Discovery

```text
list_nodes
list_topics
topic_info
node_info
list_services
service_info
list_parameters
get_parameter
list_interfaces
interface_info
list_actions
action_info
```

---

## Topic Operations

```text
read_topic
read_topic_messages
publish_topic
get_topic_qos
recommend_topic_qos
```

---

## Persistent Publishers

```text
create_persistent_publisher
publish_with_publisher
list_persistent_publishers
destroy_persistent_publisher
```

---

## Services

```text
list_services
service_info
call_service
```

---

## Parameters

```text
list_parameters
get_parameter
set_parameter
```

---

## Actions

```text
list_actions
action_info
send_action_goal
start_action_goal
get_action_status
cancel_action_goal
```

---

## Runtime Observability

```text
read_rosout
get_diagnostics
get_runtime_health
```

---

## Interface Discovery

```text
list_interfaces
interface_info
```

---

## Process Management

```text
start_ros_process
get_ros_process
list_ros_processes
stop_ros_process
```

---

## Launch Management

```text
start_ros_launch
get_ros_launch
list_ros_launches
stop_ros_launch
```

---

## Lifecycle Management

```text
get_lifecycle_state
change_lifecycle_state
```

---

## rosbag2 Management

```text
start_bag_recording
stop_bag_recording
get_bag_info
start_bag_playback
stop_bag_playback
```

---

## Safety

```text
get_safety_guardrails
```

---

# ROS Graph Discovery

## `list_nodes`

Lists currently discovered ROS 2 nodes.

---

## `list_topics`

Lists discovered topics and message types.

---

## `topic_info`

Returns information such as:

```text
topic name
topic types
publisher count
subscriber count
```

---

## `node_info`

Returns detailed node graph information.

This includes:

```text
publishers
subscribers
service servers
service clients
```

---

## `list_services`

Lists discovered services and service types.

---

## `service_info`

Returns information about a ROS 2 service and its runtime endpoints.

---

# Topic Reading

## `read_topic`

Reads one ROS topic message.

The message type is dynamically discovered and resolved.

Example result:

```json
{
  "topic": "/example",
  "type": "std_msgs/msg/String",
  "message": {
    "data": "hello"
  }
}
```

Topic reading uses automatic QoS discovery by default unless an explicit QoS profile is supplied.

---

# Multi-Message Topic Reading

## `read_topic_messages`

Collects multiple messages from a topic during a bounded observation period.

Important inputs:

```text
topic_name
max_messages
duration_sec
qos
```

Example:

```text
Topic:
/mcp_final/multi_messages

max_messages:
5

duration_sec:
2
```

A real Codex test returned exactly five messages.

Example:

```text
codex multi message 326
codex multi message 327
codex multi message 328
codex multi message 329
codex multi message 330
```

The selected QoS was:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

---

# Topic Publishing

## `publish_topic`

Publishes one structured ROS message.

Example:

```text
Topic:
/chatter

Type:
std_msgs/msg/String
```

Message:

```json
{
  "data": "hello from ros2_mcp"
}
```

The message type is dynamically resolved.

Safety checks are applied before the write operation.

---

# Persistent Publishers

Phase 7 adds a managed publisher registry.

Tools:

```text
create_persistent_publisher
publish_with_publisher
list_persistent_publishers
destroy_persistent_publisher
```

The lifecycle is:

```text
create_persistent_publisher
        |
        v
publisher_id
        |
        +--> publish
        +--> publish
        +--> publish
        |
        v
destroy_persistent_publisher
```

The registry stores information such as:

```text
publisher_id
topic
type
QoS
publish_count
subscriber_count
```

A real subscriber successfully received multiple messages from the same persistent publisher.

---

# QoS Support

ROS 2 communication depends on DDS QoS compatibility.

Supported QoS properties include:

```text
history
depth
reliability
durability
```

Supported reliability values:

```text
reliable
best_effort
```

Supported durability values:

```text
volatile
transient_local
```

Supported history values:

```text
keep_last
keep_all
```

Invalid profiles are rejected.

---

# QoS Inspection

## `get_topic_qos`

Discovers QoS profiles used by current publishers and subscriptions.

Example:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

---

# QoS Recommendation

## `recommend_topic_qos`

Generates a recommended profile for the requested role.

Example:

```text
role:
subscription
```

A BEST_EFFORT publisher with depth 7 resulted in:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

---

# Automatic QoS Selection

A real Codex integration test exposed an important QoS problem.

The publisher used:

```text
BEST_EFFORT
VOLATILE
KEEP_LAST
depth 7
```

The original default reader attempted:

```text
RELIABLE
VOLATILE
KEEP_LAST
depth 10
```

ROS 2 reported:

```text
incompatible QoS
Last incompatible policy: RELIABILITY
```

The reader returned:

```text
message: null
```

The implementation was corrected so that topic reading automatically derives a compatible QoS profile when no explicit QoS configuration is supplied.

A real verification then returned:

```json
{
  "message": {
    "data": "auto qos fixed 6"
  },
  "qos": {
    "history": "keep_last",
    "depth": 7,
    "reliability": "best_effort",
    "durability": "volatile"
  }
}
```

Final result:

```text
DEFAULT AUTO-QoS TEST: PASSED
```

---

# Service Calls

## `call_service`

Calls a ROS 2 service using structured input.

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

Verified response:

```json
{
  "success": true,
  "message": "enabled"
}
```

The service type is dynamically resolved.

---

# Parameter Operations

## `list_parameters`

Lists parameters exposed by a ROS node.

---

## `get_parameter`

Reads one parameter.

---

## `set_parameter`

Changes one parameter.

Example:

```text
Node:
/mcp_parameter_test

Parameter:
enabled

Value:
true
```

Independent ROS 2 verification confirmed:

```text
Boolean value is: True
```

---

# ROS Action Support

The runtime supports both synchronous and managed action execution.

---

## `send_action_goal`

Sends a goal and waits for completion.

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

Verified result:

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

---

# Action Discovery

## `list_actions`

Discovers active ROS 2 actions.

Verified example:

```text
/mcp_final/fibonacci
example_interfaces/action/Fibonacci
```

---

# Action Inspection

## `action_info`

Returns structured information including:

```text
name
types
server_count
client_count
servers
clients
transport endpoints
```

Verified server:

```text
/mcp_final_codex_server
```

The action transport includes endpoints such as:

```text
_action/send_goal
_action/get_result
_action/cancel_goal
_action/feedback
_action/status
```

---

# Managed Action Goals

Long-running actions can be managed across multiple MCP calls.

Tools:

```text
start_action_goal
get_action_status
cancel_action_goal
```

Conceptually:

```text
start_action_goal
        |
        v
goal_id
        |
        +--> get_action_status
        +--> get_action_status
        |
        v
cancel_action_goal
        |
        v
get_action_status
```

Stored information includes:

```text
goal_id
action
type
goal
status
status_name
feedback
result
completed
```

A real test verified the action states:

```text
EXECUTING
CANCELING
CANCELED
```

---

# Interface Discovery

## `list_interfaces`

Lists installed:

```text
messages
services
actions
```

Interfaces can be filtered by:

```text
package
interface kind
```

---

## `interface_info`

Returns structured interface information.

Example message:

```text
std_msgs/msg/String
```

Result:

```text
kind: msg

fields:
data: string
```

Example service:

```text
std_srvs/srv/SetBool
```

Result contains:

```text
request
response
```

Example action:

```text
example_interfaces/action/Fibonacci
```

Result contains:

```text
goal
result
feedback
```

---

# ROS Logging

## `read_rosout`

Reads structured ROS log messages from:

```text
/rosout
```

Filtering supports:

```text
node
minimum severity
maximum number of messages
```

Example verified ERROR messages:

```text
codex rosout error 14
codex rosout error 15
codex rosout error 16
codex rosout error 17
codex rosout error 18
codex rosout error 19
```

Codex successfully retrieved the log entries using only `ros2_mcp`.

---

# Diagnostics

## `get_diagnostics`

Reads ROS diagnostics from:

```text
/diagnostics
```

using:

```text
diagnostic_msgs/msg/DiagnosticArray
```

Supported levels:

```text
OK
WARN
ERROR
STALE
```

A ROS 2 Jazzy compatibility issue involving the generated Python representation of `DiagnosticStatus.level` was discovered during real testing and corrected.

---

# Runtime Health

## `get_runtime_health`

Combines:

```text
ROS graph
diagnostics
rosout
```

into one compact runtime health summary.

Example:

```text
health: ERROR

graph:
    nodes: 3
    services: 14
    topics: 3

diagnostics:
    OK: 0
    WARN: 4
    ERROR: 4
    STALE: 0

rosout:
    warn: 3
    error: 2
    fatal: 0
```

Possible overall states include:

```text
OK
WARN
ERROR
```

---

# Executor Serialization

A real Codex test exposed concurrent executor access.

Observed error:

```text
Executor is already spinning
```

Multiple MCP requests were attempting to spin the shared ROS executor concurrently.

The Jazzy adapter now serializes executor access using a shared lock.

Executor operations are centralized through adapter helper methods.

A concurrent verification executed:

```text
get_runtime_health
list_nodes
list_topics
get_runtime_health
```

successfully.

Final result:

```text
CONCURRENT EXECUTOR TEST: PASSED
```

---

# ROS Process Management

Tools:

```text
start_ros_process
get_ros_process
list_ros_processes
stop_ros_process
```

Processes are resolved through ROS package information.

The runtime does not expose arbitrary shell execution.

Dry-run example:

```text
package:
demo_nodes_cpp

executable:
talker
```

Resolved executable:

```text
/opt/ros/jazzy/lib/demo_nodes_cpp/talker
```

Result:

```text
dry_run: true
```

---

# ROS Launch Management

Tools:

```text
start_ros_launch
get_ros_launch
list_ros_launches
stop_ros_launch
```

Launch files are resolved through installed ROS packages and the ament index.

A real test package was registered temporarily and used to start:

```text
mcp_launch_test_talker
```

The full lifecycle passed:

```text
START
GET
LIST
STOP
LIST AFTER STOP
```

Final result:

```text
REAL LAUNCH MANAGEMENT TEST: PASSED
```

---

# Lifecycle Node Management

Tools:

```text
get_lifecycle_state
change_lifecycle_state
```

Verified transitions included:

```text
unconfigured
    |
    v
inactive
    |
    v
active
    |
    v
inactive
    |
    v
unconfigured
```

The lifecycle test successfully performed:

```text
configure
activate
deactivate
cleanup
```

---

# rosbag2 Management

Recording tools:

```text
start_bag_recording
stop_bag_recording
get_bag_info
```

Playback tools:

```text
start_bag_playback
stop_bag_playback
```

A real recording test captured messages from:

```text
/mcp_bag_test
```

The recorded bag was inspected and subsequently played back.

Managed bag names are validated by the safety layer.

Dry-run mode is also available.

---

# Safety Model

Phase 7 introduces explicit runtime guardrails.

Safety implementation:

```text
src/ros2_mcp/ros/jazzy/safety.py
```

Configuration:

```text
config/ros2_mcp.toml
```

Configuration loader:

```text
src/ros2_mcp/config/settings.py
```

---

# No Arbitrary Shell

The active policy reports:

```text
arbitrary_shell: false
```

The runtime exposes explicit ROS operations instead of shell commands.

---

# Managed Stop Policies

Safety reports:

```text
managed_process_stop_only: true
managed_launch_stop_only: true
managed_rosbag_stop_only: true
```

Only resources managed by this MCP server can be stopped through these operations.

---

# Package and Launch Resolution

Safety reports:

```text
package_resolution_required: true
launch_file_resolution_required: true
```

Managed process and launch execution must resolve through ROS package infrastructure.

---

# Path Traversal Protection

Unsafe resource names are rejected.

Examples:

```text
../bad
```

Negative tests verified:

```text
process traversal blocked: True
bag traversal blocked: True
```

---

# Structured Argument Validation

Process arguments are passed as structured lists instead of shell strings.

Validation rejects:

```text
NUL characters
newlines
carriage returns
oversized arguments
excessive argument counts
```

---

# Protected ROS Topics

Current protected topics include:

```text
/parameter_events
/rosout
```

Writing directly to these topics is blocked.

Verified result:

```text
protected /rosout blocked: True
```

---

# Configurable Safety Policies

Configuration supports:

```text
protected_topics
protected_services
protected_parameters
protected_actions

allowed_process_packages
allowed_launch_packages
```

This allows installations to apply tighter policies without changing the implementation.

---

# Runtime Resource Limits

Current configured limits include:

```text
persistent_publishers: 32
managed_processes: 16
managed_launches: 8
bag_recordings: 4
bag_playbacks: 4
```

These limits prevent unbounded resource creation.

---

# Dry-Run Support

Dry-run mode is available for:

```text
start_ros_process
start_ros_launch
start_bag_recording
start_bag_playback
```

This allows an MCP client to validate an operation before actually starting a runtime resource.

---

# Safety Inspection

## `get_safety_guardrails`

Returns the active runtime safety configuration.

Important information includes:

```text
shell policy
managed stop policy
protected resources
allowed packages
resource limits
dry-run support
```

---

# Development Environment

Current development environment:

```text
Ubuntu 24.04
ROS 2 Jazzy
Python 3.12
uv
MCP Python SDK
Cyclone DDS
```

---

# Environment Setup

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

When explicitly configuring the project ROS domain:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

# Install Dependencies

```bash
cd ~/projects/robotics/ros2_mcp

uv sync
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

---

# Run the MCP Server

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m ros2_mcp.server
```

The server uses MCP standard I/O transport.

---

# Syntax Check

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
```

Expected:

```text
exit code 0
```

---

# Runtime Tests

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q
```

Final verified Phase 7 result:

```text
...........                                                      [100%]

11 passed
```

---

# Complete Local Verification

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
```

Expected:

```text
11 passed
```

---

# MCP Tool Inventory Test

The registered MCP tools can be queried directly.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import asyncio

from mcp import Client
from ros2_mcp.server import create_server


async def main() -> None:
    """Print all registered ros2_mcp tools."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.list_tools()

        names = sorted(
            tool.name
            for tool in result.tools
        )

        print("Tool count:", len(names))

        for name in names:
            print(name)


asyncio.run(main())
PY
```

Expected final result:

```text
Tool count: 46
```

---

# Adapter Contract Check

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from ros2_mcp.ros.jazzy.adapter import JazzyRosAdapter


print(
    "Abstract methods:",
    sorted(JazzyRosAdapter.__abstractmethods__),
)

if JazzyRosAdapter.__abstractmethods__:
    raise RuntimeError(
        "JazzyRosAdapter does not implement the complete RosAdapter contract."
    )

print("JazzyRosAdapter contract: OK")
PY
```

Expected:

```text
Abstract methods: []
JazzyRosAdapter contract: OK
```

---

# Adapter Structure Check

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

wc -l src/ros2_mcp/ros/jazzy/adapter.py

find src/ros2_mcp/ros/jazzy \
  -maxdepth 1 \
  -type f \
  -printf '%f\n' \
  | sort
```

The implementation should remain modular.

---

# Safety Guardrail Check

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from pprint import pprint

from ros2_mcp.ros.jazzy.adapter import JazzyRosAdapter


adapter = JazzyRosAdapter()

try:
    pprint(
        adapter.get_safety_guardrails()
    )
finally:
    adapter.close()
PY
```

---

# Codex Integration

Register the local MCP server with Codex.

Example:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp add ros2_mcp \
  --env ROS_DOMAIN_ID=30 \
  --env RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -- \
  bash -lc 'cd /home/sarvg/projects/robotics/ros2_mcp && source /opt/ros/jazzy/setup.bash && source .venv/bin/activate && exec python -m ros2_mcp.server'
```

Inspect the registration:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2_mcp
```

Start Codex:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
```

Inside Codex:

```text
/mcp
```

---

# Codex Usage Rule

For runtime-only tests, Codex can be explicitly instructed:

```text
Use only ros2_mcp.

Do not use shell commands.
Do not modify files.
Do not use ros2_dev_mcp.
```

This makes it possible to verify that Codex selects the runtime MCP instead of falling back to the shell or development server.

---

# Verified Codex Runtime Operations

Codex has successfully exercised runtime operations including:

```text
list_nodes
topic_info
publish_topic
call_service
set_parameter
send_action_goal
read_rosout
interface_info
list_interfaces
get_topic_qos
recommend_topic_qos
get_runtime_health
get_safety_guardrails
start_ros_process with dry_run
list_actions
action_info
read_topic_messages
```

---

# Final Codex Action and Multi-Message Test

A final integration environment exposed:

```text
Action:
/mcp_final/fibonacci

Action type:
example_interfaces/action/Fibonacci

Server:
/mcp_final_codex_server
```

and:

```text
Topic:
/mcp_final/multi_messages
```

Codex was instructed:

```text
Use only ros2_mcp.

Perform the final verification of the three new ROS 2 core tools.

1. List all currently discovered ROS 2 actions.

2. Inspect this action:
   /mcp_final/fibonacci

3. Read exactly 5 messages from:
   /mcp_final/multi_messages

Use automatic QoS selection.
Use a maximum duration of 2 seconds.

Do not use shell commands.
Do not modify files.
Do not use ros2_dev_mcp.
```

Codex selected:

```text
list_actions
action_info
read_topic_messages
```

All operations succeeded.

Five messages were received:

```text
codex multi message 326
codex multi message 327
codex multi message 328
codex multi message 329
codex multi message 330
```

QoS:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

Final Codex result:

```text
Every operation succeeded: Yes
```

---

# Real ROS 2 Verification

The implementation has been tested against a real ROS 2 Jazzy runtime.

Verified areas include:

```text
ROS graph discovery

topic inspection
topic reading
multi-message topic reading
topic publishing

service calls

parameter writes

action execution
action feedback
action results
action cancellation
action discovery
action inspection

interface discovery

rosout filtering
diagnostics
runtime health

QoS discovery
QoS recommendation
automatic QoS

persistent publishers

process management
launch management
lifecycle operations

rosbag recording
rosbag playback

safety rejection tests

executor concurrency
```

---

# Important Runtime Issues Found and Fixed

Real runtime testing exposed several issues that unit testing alone did not reveal.

## Diagnostic Level Representation

ROS diagnostic severity values required normalization before integer comparison.

Status:

```text
FIXED
```

---

## Auto-QoS Compatibility

A RELIABLE subscription could not receive from a BEST_EFFORT publisher.

Status:

```text
FIXED
```

Default topic reading now automatically derives a compatible profile.

---

## Executor Concurrency

Concurrent MCP calls produced:

```text
Executor is already spinning
```

Status:

```text
FIXED
```

Executor access is now serialized.

---

## Launch Package Resolution

The launch integration test initially used an incomplete temporary ament package registration.

The test environment was corrected to use the ament resource index.

Status:

```text
FIXED
REAL LAUNCH MANAGEMENT TEST: PASSED
```

---

# Documentation

Runtime development documentation is stored in:

```text
docs/
├── README_PHASE_1.md
├── README_PHASE_2.md
├── README_PHASE_3.md
├── README_PHASE_4.md
├── README_PHASE_5.md
├── README_PHASE_6.md
└── README_PHASE_7.md
```

Phase 6 documents the controlled interaction foundation.

Phase 7 documents the advanced runtime, observability, safety, management, QoS, modularization, and final integration work.

---

# Completed Runtime Capabilities

```text
ROS graph discovery            ✅
Node inspection                ✅

Topic discovery                ✅
Topic information              ✅
Single-message reading         ✅
Multi-message reading          ✅
Topic publishing               ✅

QoS configuration              ✅
QoS inspection                 ✅
QoS recommendation             ✅
Automatic QoS                  ✅

Persistent publishers          ✅

Service discovery              ✅
Service information            ✅
Service calls                  ✅

Parameter discovery            ✅
Parameter reading              ✅
Parameter writing              ✅

Action discovery               ✅
Action information             ✅
Action goals                   ✅
Action feedback                ✅
Action results                 ✅
Managed action sessions        ✅
Action status                  ✅
Action cancellation            ✅

Interface discovery            ✅
Interface inspection           ✅

ROS logging                    ✅
Diagnostics                    ✅
Runtime health                 ✅

Process management             ✅
Launch management              ✅
Lifecycle operations           ✅

rosbag recording               ✅
rosbag playback                ✅
rosbag information             ✅

Safety guardrails              ✅
Runtime limits                 ✅
Dry-run validation             ✅

Executor serialization         ✅

Codex MCP integration          ✅
Runtime / Dev separation       ✅
Real ROS 2 verification        ✅
```

---

# Verified Final Status

```text
MCP tools:
46

Unit/regression tests:
11 passed

Python syntax:
PASS

Real ROS 2 integration:
PASS

Codex integration:
PASS
```

---

# Current Limitations and Intentional Boundaries

The following capabilities are intentionally outside the generic `ros2_mcp` scope:

```text
ROS 1 compatibility

arbitrary shell execution
arbitrary ROS CLI execution

ROS project generation
ROS package generation
source-code creation
build workflows
development tests

camera image retrieval
camera-specific processing
LiDAR-specific processing

ros2_control-specific semantics
Nav2-specific semantics
MoveIt 2-specific semantics

robot-specific physical safety
controller-specific safety
navigation-specific safety
manipulation-specific safety
```

These are not considered missing generic runtime features.

They belong to separate development or specialized robotics MCP servers.

---

# Image Retrieval Boundary

Camera and image retrieval are intentionally not implemented directly in `ros2_mcp`.

A future specialized MCP can provide:

```text
mcp_camera
```

Possible responsibilities:

```text
image retrieval
depth images
camera info
camera configuration
stream selection
camera metadata
point-cloud conversion
camera-specific diagnostics
```

Possible future hardware:

```text
Intel RealSense
Luxonis OAK-D
Stereolabs ZED2
generic ROS image_transport cameras
```

`ros2_mcp` can still inspect the corresponding ROS topics through its normal graph and topic tools.

---

# ROS 1 Boundary

This project targets ROS 2.

ROS 1 is intentionally not supported.

The architecture is built around:

```text
ROS 2
DDS
rclpy
ROS 2 Actions
ROS 2 Lifecycle
ROS 2 QoS
ROS 2 interfaces
```

ROS 1 compatibility would require a separate runtime model and is outside the project scope.

---

# Specialized MCP Architecture

The generic runtime MCP should remain focused.

Future subsystem-specific servers can build on the generic ROS 2 runtime foundation.

```text
                    MCP Client / AI Agent
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
        ros2_mcp       ros2_dev_mcp    Specialized MCPs
            |               |               |
            v               v               |
      ROS 2 Runtime     ROS 2 Projects       |
                                            +--> ros2_control_mcp
                                            +--> ros2_nav_mcp
                                            +--> ros2_moveit_mcp
                                            +--> mcp_camera
```

---

# ros2_control MCP

Planned:

```text
ros2_control_mcp
```

Possible responsibilities:

```text
controller manager
controller states
controller switching
hardware interfaces
resource claims
joint command interfaces
joint state interfaces
hardware status
controller safety
```

These concepts should not be embedded directly into generic `ros2_mcp`.

---

# Nav2 MCP

Planned:

```text
ros2_nav_mcp
```

Possible responsibilities:

```text
navigation goals
navigation cancellation
navigation status
maps
costmaps
localization
planner selection
behavior trees
navigation safety
```

Generic Action and Lifecycle functionality from `ros2_mcp` provides the runtime foundation.

---

# MoveIt 2 MCP

Planned:

```text
ros2_moveit_mcp
```

Possible responsibilities:

```text
planning groups
robot state
joint targets
pose targets
motion planning
trajectory execution
planning scene
collision objects
manipulation safety
```

The generic ROS topic, service, parameter, action, and interface tools remain in `ros2_mcp`.

---

# Camera MCP

Planned:

```text
mcp_camera
```

Possible responsibilities:

```text
image retrieval
depth retrieval
camera info
stream management
camera configuration
camera-specific diagnostics
camera point-cloud handling
```

This separation prevents the generic ROS runtime server from becoming monolithic.

---

# Future Real Robot Integration

Once the specialized MCP servers are available, realistic robot scenarios can be built.

Examples include:

```text
TurtleBot3
OpenManipulator-X
RealSense
OAK-D
ZED2
LiDAR
motors
servos
robot controllers
navigation
motion planning
perception
```

Conceptually:

```text
LLM / MCP Client
        |
        v
Specialized MCP
        |
        v
ros2_mcp Runtime Foundation
        |
        v
ROS 2
        |
        v
Robot / Sensors / Actuators
```

---

# Project Principles

- Runtime and development tooling remain separated
- ROS access goes through a dedicated adapter
- ROS distributions should remain replaceable
- MCP clients should remain replaceable
- Read and write operations remain clearly distinguishable
- Runtime write operations are explicit
- Avoid private or unstable ROS APIs when possible
- Avoid unnecessary frameworks
- No arbitrary shell interface in the runtime MCP
- No arbitrary ROS CLI execution in the runtime MCP
- Safety policies remain explicit and inspectable
- Runtime resources remain managed and bounded
- Subsystem-specific semantics remain separate
- Implementation remains independent
- External ROS MCP projects may be evaluated for architecture and feature comparison
- External ROS MCP code is not copied into this implementation

---

# Current Project Status

```text
Phase 1   Runtime foundation                   ✅
Phase 2   ROS graph discovery                  ✅
Phase 3   Topic runtime inspection             ✅
Phase 4   Runtime architecture expansion       ✅
Phase 5   Extended runtime inspection          ✅
Phase 6   Controlled runtime interaction       ✅
Phase 7   Advanced runtime operations          ✅
```

The generic ROS 2 runtime foundation is now operational.

Final generic runtime status:

```text
46 MCP tools
11 tests passed
real ROS 2 verification passed
Codex verification passed
modular Jazzy architecture
safety guardrails enabled
```

The generic `ros2_mcp` feature scope is therefore considered complete for the current architecture.

---

# Final Repository Verification

Before committing:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q

git status
git diff --stat
```

Expected:

```text
11 passed
```

---

# Final Commit Procedure

After documentation and final verification:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git status
git diff --stat

git add \
  .gitignore \
  config/ros2_mcp.toml \
  docs/README_PHASE_7.md \
  README.md \
  src \
  tests

git status --short

git commit -m "Complete advanced ROS 2 runtime operations"

git push origin main

git status
git log --oneline -5
```

Desired final state:

```text
working tree clean
branch synchronized with origin/main
```

---

# Repository

This project is developed independently.

Other ROS MCP implementations may be evaluated for feature and architecture comparison, but their source code is not used as a copy-and-paste implementation basis.

The architecture and implementation of `ros2_mcp` are developed specifically for this project.
