# Phase 5 – Extended ROS 2 Runtime Inspection

## Goal

Phase 5 extends the ROS 2 MCP runtime with additional read-only inspection capabilities.

The goal is to allow an MCP client to inspect a running ROS 2 system without modifying its state.

Phase 5 adds:

- detailed node inspection
- parameter discovery
- parameter value reading
- detailed service inspection

All ROS 2 access continues to go through the ROS adapter.

The MCP layer does not access `rclpy` directly.

---

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
Jazzy ROS Adapter
    |
    v
rclpy
    |
    v
ROS 2 / DDS
```

The architecture keeps the following layers separated:

1. MCP layer
2. Application layer
3. ROS adapter interface
4. ROS 2 Jazzy implementation
5. ROS 2 / DDS runtime

This allows ROS-specific implementation details to remain outside the MCP and application layers.

---

## Phase 5 Runtime Tools

The following runtime inspection capabilities were added.

### `node_info`

Returns detailed graph information for a ROS 2 node.

Example:

```text
node_info("/demo_node")
```

The result contains information such as:

```text
node
publishers
subscribers
service_servers
service_clients
```

Example result:

```text
/demo_node

Publishers:
  /parameter_events
  /rosout

Service servers:
  /demo_node/describe_parameters
  /demo_node/get_parameter_types
  /demo_node/get_parameters
  /demo_node/get_type_description
  /demo_node/list_parameters
  /demo_node/set_parameters
  /demo_node/set_parameters_atomically
```

---

### `list_parameters`

Returns the parameters exposed by a ROS 2 node.

Example:

```text
list_parameters("/demo_node")
```

Verified result:

```text
start_type_description_service
use_sim_time
```

---

### `get_parameter`

Reads one parameter from a ROS 2 node.

Example:

```text
get_parameter("/demo_node", "use_sim_time")
```

Verified result:

```text
node: /demo_node
parameter: use_sim_time
type: bool
value: False
```

This operation is read-only.

---

### `service_info`

Returns information about a ROS 2 service.

Example:

```text
service_info("/demo_node/get_parameters")
```

Verified result:

```text
service: /demo_node/get_parameters
types:
  rcl_interfaces/srv/GetParameters

servers:
  /demo_node

clients: []
```

---

## Files Modified

Phase 5 extends the existing runtime architecture.

Main files:

```text
src/ros2_mcp/
├── application/
│   └── runtime/
│       └── service.py
├── mcp/
│   └── runtime_tools.py
└── ros/
    ├── adapter.py
    └── jazzy/
        └── adapter.py
```

Responsibilities:

```text
ros/adapter.py
```

Defines the distribution-independent ROS runtime interface.

```text
ros/jazzy/adapter.py
```

Implements the runtime operations using ROS 2 Jazzy and `rclpy`.

```text
application/runtime/service.py
```

Provides the application boundary between MCP and the ROS adapter.

```text
mcp/runtime_tools.py
```

Exposes the runtime operations as MCP tools.

---

# Real ROS 2 Verification

Phase 5 was verified against a real ROS 2 Jazzy runtime.

The persistent demo project created during Phase 6 was used.

Workspace:

```text
~/projects/robotics/ros2_mcp/demo_ws
```

Package:

```text
demo_robot
```

Node:

```text
/demo_node
```

---

## 1. Start the Demo Node

Open the first terminal.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source demo_ws/install/setup.bash

ros2 run demo_robot demo_node
```

The node remains running in this terminal.

---

## 2. Verify the Node from ROS 2 CLI

Open a second terminal.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source demo_ws/install/setup.bash

ros2 node list
```

Expected result:

```text
/demo_node
```

---

## 3. Inspect the Node with ROS 2 CLI

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source demo_ws/install/setup.bash

ros2 node info /demo_node
```

Verified runtime information includes:

```text
/demo_node

Publishers:
  /parameter_events
  /rosout

Subscribers:

Service Servers:
  /demo_node/describe_parameters
  /demo_node/get_parameter_types
  /demo_node/get_parameters
  /demo_node/get_type_description
  /demo_node/list_parameters
  /demo_node/set_parameters
  /demo_node/set_parameters_atomically

Service Clients:

Action Servers:

Action Clients:
```

---

## 4. Verify Parameters with ROS 2 CLI

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source demo_ws/install/setup.bash

printf '\n--- Parameters ---\n'
ros2 param list /demo_node

printf '\n--- use_sim_time ---\n'
ros2 param get /demo_node use_sim_time
```

Verified result:

```text
--- Parameters ---
  start_type_description_service
  use_sim_time

--- use_sim_time ---
Boolean value is: False
```

---

## 5. Verify a Service with ROS 2 CLI

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source demo_ws/install/setup.bash

ros2 service type /demo_node/get_parameters
```

Verified result:

```text
rcl_interfaces/srv/GetParameters
```

---

# MCP Runtime Verification

The new functionality was also tested through the actual MCP server.

This verifies the complete path:

```text
MCP Client
    ->
MCP Tool
    ->
Runtime Service
    ->
ROS Adapter
    ->
rclpy
    ->
ROS 2
```

---

## Verify Available MCP Runtime Tools

The MCP runtime now provides the existing runtime tools plus the Phase 5 inspection tools.

Relevant Phase 5 tools:

```text
node_info
list_parameters
get_parameter
service_info
```

---

## Real MCP `node_info`

The following call was verified against the running `/demo_node`.

```text
node_info("/demo_node")
```

Verified result:

```text
{
    "node": "/demo_node",
    "publishers": [
        {
            "name": "/parameter_events",
            "types": [
                "rcl_interfaces/msg/ParameterEvent"
            ]
        },
        {
            "name": "/rosout",
            "types": [
                "rcl_interfaces/msg/Log"
            ]
        }
    ],
    "subscribers": [],
    "service_servers": [
        {
            "name": "/demo_node/describe_parameters",
            "types": [
                "rcl_interfaces/srv/DescribeParameters"
            ]
        },
        {
            "name": "/demo_node/get_parameter_types",
            "types": [
                "rcl_interfaces/srv/GetParameterTypes"
            ]
        },
        {
            "name": "/demo_node/get_parameters",
            "types": [
                "rcl_interfaces/srv/GetParameters"
            ]
        },
        {
            "name": "/demo_node/get_type_description",
            "types": [
                "type_description_interfaces/srv/GetTypeDescription"
            ]
        },
        {
            "name": "/demo_node/list_parameters",
            "types": [
                "rcl_interfaces/srv/ListParameters"
            ]
        },
        {
            "name": "/demo_node/set_parameters",
            "types": [
                "rcl_interfaces/srv/SetParameters"
            ]
        },
        {
            "name": "/demo_node/set_parameters_atomically",
            "types": [
                "rcl_interfaces/srv/SetParametersAtomically"
            ]
        }
    ],
    "service_clients": []
}
```

---

## Real MCP `list_parameters`

Call:

```text
list_parameters("/demo_node")
```

Verified result:

```text
{
    "result": [
        "start_type_description_service",
        "use_sim_time"
    ]
}
```

---

## Real MCP `get_parameter`

Call:

```text
get_parameter(
    "/demo_node",
    "use_sim_time"
)
```

Verified result:

```text
{
    "node": "/demo_node",
    "parameter": "use_sim_time",
    "type": "bool",
    "value": false
}
```

---

## Real MCP `service_info`

Call:

```text
service_info(
    "/demo_node/get_parameters"
)
```

Verified result:

```text
{
    "service": "/demo_node/get_parameters",
    "types": [
        "rcl_interfaces/srv/GetParameters"
    ],
    "servers": [
        "/demo_node"
    ],
    "clients": []
}
```

---

# ROS Discovery Behavior

During Phase 5 development an important ROS 2 runtime behavior was identified.

Immediately after creating the ROS adapter, the ROS graph may not yet contain remote nodes.

For example, immediately after adapter creation only the internal runtime node was visible:

```text
[
    ("ros2_mcp_runtime", "/")
]
```

After spinning the ROS executor, DDS discovery found the running demo node:

```text
[
    ("ros2_mcp_runtime", "/"),
    ("demo_node", "/"),
    ("_ros2cli_daemon_...", "/")
]
```

The implementation therefore needs to allow ROS discovery to occur before requesting detailed information about a remote node.

This was verified with the real `/demo_node`.

---

# Node Name Handling

ROS graph APIs expect the node name and namespace separately.

The external MCP interface can use a normal fully qualified ROS node name:

```text
/demo_node
```

The Jazzy adapter normalizes this before calling the corresponding `rclpy` graph APIs.

This prevents invalid node-name errors caused by passing the leading `/` as part of the node name.

---

# Action Discovery

Action discovery was investigated during Phase 5.

The ROS 2 CLI supports:

```bash
ros2 action list
```

However, the `rclpy.node.Node` API used by the current adapter does not expose action discovery through the same public graph methods used for:

```text
nodes
topics
services
publishers
subscribers
```

An attempted direct implementation was therefore removed.

Phase 5 does **not** expose a `list_actions` MCP tool.

This is intentional.

Action support should be implemented later using an appropriate ROS 2 action-specific API rather than relying on unsupported or incorrect assumptions.

---

# Safety

Phase 5 remains read-only.

The following operations inspect the ROS graph or read runtime state:

```text
node_info
list_parameters
get_parameter
service_info
```

They do not:

```text
publish messages
change parameters
call arbitrary services
send action goals
start nodes
stop nodes
modify ROS projects
execute arbitrary shell commands
```

Write operations remain outside the Phase 5 runtime interface.

---

# Quick Manual Verification

With `/demo_node` running, the essential Phase 5 runtime checks can be repeated with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source demo_ws/install/setup.bash

printf '\n--- Nodes ---\n'
ros2 node list

printf '\n--- Node info ---\n'
ros2 node info /demo_node

printf '\n--- Parameters ---\n'
ros2 param list /demo_node

printf '\n--- Parameter value ---\n'
ros2 param get /demo_node use_sim_time

printf '\n--- Service type ---\n'
ros2 service type /demo_node/get_parameters
```

Expected essential results:

```text
/demo_node

start_type_description_service
use_sim_time

Boolean value is: False

rcl_interfaces/srv/GetParameters
```

---

# Minimal Development Check

The project can be syntax-checked with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate

python -m compileall -q src
```

A full test run remains available when needed:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate

pytest -q
```

For Phase 5, real ROS 2 runtime verification is considered more important than adding large numbers of isolated unit tests.

---

# Phase 5 Result

Phase 5 extends `ros2_mcp` from basic ROS graph discovery and topic reading into more useful runtime inspection.

The MCP server can now inspect:

```text
ROS System
│
├── Nodes
│   └── detailed node information
│
├── Topics
│   └── read topic data
│
├── Parameters
│   ├── list parameters
│   └── read parameter values
│
└── Services
    └── inspect service information
```

The functionality was verified against a real ROS 2 Jazzy node and through the actual MCP server.

Phase 5 is complete.

---

# Next Phase

## Phase 6 – Controlled Write and Deployment Readiness

Phase 6 will introduce carefully controlled write capabilities.

Possible areas include:

```text
publish_topic
set_parameter
call_service
```

Write operations must not simply expose unrestricted ROS access.

Phase 6 should define explicit safety policies for:

- allowed operations
- allowed topics
- allowed services
- allowed parameters
- message validation
- timeouts
- error handling
- dangerous-operation restrictions

After the controlled write layer is stable, deployment topics such as Docker and later Kubernetes can be addressed.
