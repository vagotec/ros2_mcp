# Phase 9 – MCP 2026-07-28 Protocol Compliance

## 1. Goal

Phase 9 verifies that `ros2_mcp` operates correctly with the MCP protocol baseline:

```text
2026-07-28
```

The purpose of this phase is to establish a permanent protocol compliance regression test before extending the MCP server with additional MCP capabilities such as:

- Server Instructions
- MCP Prompts
- MCP Resources
- Client compatibility testing
- Remote MCP / HTTP transport

Phase 9 does not add new ROS 2 functionality.

It establishes and verifies the MCP protocol baseline for the existing `ros2_mcp` server.

---

## 2. Development Branch

Phase 9 is developed on:

```text
dev
```

The stable Version 1 implementation remains on:

```text
main
```

Future MCP extensions are developed and tested on `dev` before they are merged into `main`.

---

## 3. MCP Protocol Baseline

The required MCP protocol version for Phase 9 is:

```text
2026-07-28
```

The integration test explicitly creates the MCP client using:

```python
async with Client(
    server,
    raise_exceptions=True,
    mode="2026-07-28",
) as client:
```

The negotiated client protocol is then verified:

```python
assert client.protocol_version == "2026-07-28"
assert client.mode == "2026-07-28"
```

This prevents future changes from silently moving the server integration away from the required MCP protocol baseline.

---

## 4. Current MCP Server Architecture

The existing architecture remains unchanged:

```text
MCP Client
    │
    │ MCP
    ▼
ros2_mcp MCP Server
    │
    ├── MCP Tools
    │
    ▼
Application Runtime Service
    │
    ▼
ROS Adapter Interface
    │
    ▼
ROS 2 Jazzy Adapter
    │
    ├── Graph
    ├── Topics
    ├── Services
    ├── Actions
    ├── Parameters
    ├── Lifecycle
    ├── Interfaces
    ├── Diagnostics
    ├── Logging
    ├── QoS
    ├── Publishers
    ├── Processes
    ├── Launches
    ├── rosbag
    └── Safety
            │
            ▼
        ROS 2 Jazzy
```

Phase 9 does not change this architecture.

---

## 5. Existing MCP Tool Inventory

The server currently exposes:

```text
46 MCP tools
```

Phase 9 permanently verifies this tool count.

The compliance test also verifies representative tools from the existing functional areas.

Required representative tools include:

```text
list_nodes
list_topics
list_actions
read_topic
read_topic_messages
get_runtime_health
get_safety_guardrails
start_ros_process
```

This ensures that protocol compliance testing does not accidentally remove or hide existing ROS 2 MCP functionality.

---

## 6. Real MCP Operations

Phase 9 does not only inspect Python classes.

It enters the real MCP server lifespan and performs MCP operations through the MCP client.

The test executes:

```python
result = await client.list_tools()
```

It also executes representative server tools:

```text
get_safety_guardrails
get_runtime_health
```

These calls verify that the MCP client can communicate with the existing `ros2_mcp` server while operating in MCP protocol mode:

```text
2026-07-28
```

---

## 7. Tool Schema Verification

Phase 9 verifies that representative MCP tools expose structured input schemas.

### list_nodes

Expected characteristics:

```text
type: object
properties: {}
```

This verifies a tool without input arguments.

### read_topic

The schema must contain:

```text
topic_name
```

and `topic_name` must be required.

### start_ros_process

The schema must expose:

```text
package_name
executable
arguments
dry_run
```

Required fields:

```text
package_name
executable
```

This is especially important for controlled process management because MCP clients must receive a structured contract rather than arbitrary command execution.

### get_safety_guardrails

Expected characteristics:

```text
type: object
properties: {}
```

---

## 8. Safety Verification

Phase 9 executes:

```text
get_safety_guardrails
```

through the MCP client.

The operation must complete without an MCP error and return content.

This provides a permanent regression check that the safety interface remains reachable through the MCP protocol.

The existing safety architecture remains responsible for restrictions such as:

```text
arbitrary_shell = false
managed_process_stop_only = true
managed_launch_stop_only = true
managed_rosbag_stop_only = true
package_resolution_required = true
launch_file_resolution_required = true
structured_argument_validation = true
```

Phase 9 does not weaken or bypass these controls.

---

## 9. Runtime Health Verification

Phase 9 executes:

```text
get_runtime_health
```

through the MCP client.

The call must:

```text
complete without MCP error
return MCP content
```

This verifies a representative diagnostics/runtime operation over the required MCP protocol baseline.

---

## 10. Important MCP SDK Observation

During Phase 9 diagnosis, the following behavior was observed with:

```text
mcp 2.0.0
mcp-types 2.0.0
```

When using the direct in-process client:

```python
Client(
    server,
    raise_exceptions=True,
    mode="2026-07-28",
)
```

the client reports:

```text
protocol_version = "2026-07-28"
mode = "2026-07-28"
```

but:

```text
server_info = None
```

and the individual fields inside:

```text
server_capabilities
```

are not populated by this direct client mode.

Therefore Phase 9 intentionally does not use assertions such as:

```python
assert client.server_info is not None
```

or:

```python
assert client.server_capabilities.tools is not None
```

Those assertions would test assumptions about SDK metadata population rather than the actual protocol operations required by `ros2_mcp`.

Instead, Phase 9 verifies:

```text
explicit protocol mode
negotiated protocol version
tool discovery
tool inventory
tool schemas
real MCP tool execution
existing ROS 2 regression compatibility
```

---

## 11. Permanent Compliance Test

The permanent integration test is located at:

```text
tests/integration/test_mcp_protocol_2026_07_28.py
```

It contains two tests:

```text
test_mcp_2026_07_28_protocol_baseline
test_mcp_2026_07_28_tool_schemas
```

The first verifies protocol operation and representative MCP calls.

The second verifies representative structured MCP tool schemas.

---

## 12. Phase 9 Test Result

The dedicated Phase 9 test result is:

```text
2 passed
```

The complete project regression suite result after adding Phase 9 is:

```text
22 passed
```

Test collection:

```text
22 tests collected
```

Additional checks:

```text
Python syntax: PASS
Full pytest suite: PASS
Test collection: PASS
git diff --check: PASS
```

---

## 13. Regression Protection

Phase 9 protects the project against several future regressions.

It detects if:

- the required MCP protocol baseline changes unexpectedly,
- MCP tool discovery stops working,
- existing tools disappear,
- the expected tool count changes unexpectedly,
- representative tool schemas become malformed,
- required tool arguments disappear,
- runtime health becomes inaccessible through MCP,
- safety guardrails become inaccessible through MCP.

The test therefore becomes part of the permanent regression suite.

---

## 14. What Phase 9 Does Not Implement

Phase 9 is intentionally limited to the protocol compliance baseline.

The following capabilities are not implemented by this phase:

```text
MCP Prompts
Server Instructions
MCP Resources
Remote MCP / HTTP
Windows remote client support
macOS remote client support
multi-client compatibility testing
```

These capabilities belong to subsequent development phases.

---

## 15. Planned MCP Extension Sequence

After establishing the protocol baseline, development can continue in the following order:

```text
Phase 9
MCP 2026-07-28 Compliance
        │
        ▼
Server Instructions
        │
        ▼
MCP Prompts
        │
        ▼
MCP Resources
        │
        ▼
Client Compatibility Tests
        │
        ▼
Remote MCP / HTTP
```

The existing ROS 2 runtime remains the foundation underneath these MCP capabilities.

---

## 16. Why Compliance Comes First

Protocol compliance is implemented before the additional MCP features because all later functionality depends on a stable MCP foundation.

For example:

```text
MCP Prompts
     │
     └── depend on MCP protocol behavior

MCP Resources
     │
     └── depend on MCP protocol behavior

Remote MCP / HTTP
     │
     └── depends on MCP protocol behavior

Client Compatibility
     │
     └── depends on predictable protocol behavior
```

This allows future failures to be separated into:

```text
ROS 2 runtime problem
MCP protocol problem
MCP feature problem
transport problem
client compatibility problem
```

---

## 17. Phase 9 Final Status

Current verified status:

```text
Branch: dev

MCP SDK: 2.0.0
MCP Types: 2.0.0
MCP protocol baseline: 2026-07-28

MCP tools: 46

Dedicated Phase 9 tests: 2 passed
Complete regression suite: 22 passed

Protocol mode verification: PASS
Protocol version verification: PASS
Tool discovery: PASS
Tool inventory: PASS
Tool schema verification: PASS
Safety MCP operation: PASS
Runtime health MCP operation: PASS
Python syntax: PASS
Regression suite: PASS
Diff quality: PASS
```

## Phase 9 Result

```text
PHASE 9 MCP 2026-07-28 COMPLIANCE: PASS
```

The `ros2_mcp` project now has a permanent regression baseline for MCP protocol version `2026-07-28`.

No existing ROS 2 functionality was intentionally changed by Phase 9.
