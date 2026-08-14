# Phase 13 – Client Compatibility Tests

## 1. Goal

Phase 13 validates `ros2_mcp` with a real external MCP client.

The primary client used in this phase is:

```text
OpenAI Codex CLI
v0.147.0
```

The purpose of Phase 13 is not to add new ROS 2 functionality.

Instead, the phase verifies that the existing MCP capabilities implemented in the previous phases can be discovered and used correctly by a real MCP client.

Phase 13 builds on:

```text
Phase 9
MCP 2026-07-28 Protocol Compliance
        │
        ▼
Phase 10
Server Instructions
        │
        ▼
Phase 11
MCP Prompts
        │
        ▼
Phase 12
MCP Resources
        │
        ▼
Phase 13
Client Compatibility Tests
```

The existing ROS 2 runtime implementation remains unchanged.

No new ROS 2 runtime capability is introduced in this phase.

---

## 2. Development Branch

Phase 13 is developed and tested on:

```text
dev
```

The stable implementation remains on:

```text
main
```

The development checkout is:

```text
~/projects/robotics/ros2_mcp
```

Phase 13 performs compatibility testing against the current `dev` implementation before later Version 2 work continues.

---

## 3. MCP Protocol Baseline

The required MCP protocol baseline remains:

```text
2026-07-28
```

The installed MCP Python SDK used during Phase 13 is:

```text
mcp: 2.0.0
```

Phase 13 does not change the protocol baseline established by Phase 9.

---

## 4. MCP Capability Baseline

The MCP server entering Phase 13 exposes:

```text
Server Instructions:   enabled
MCP Tools:             46
MCP Prompts:            6
Static Resources:       0
Resource Templates:     9
```

The nine Resource Templates are:

```text
ros2://runtime/health/{scope}
ros2://runtime/safety/{scope}

ros2://graph/nodes/{scope}
ros2://graph/topics/{scope}
ros2://graph/services/{scope}
ros2://graph/actions/{scope}

ros2://node/{node_name}
ros2://topic/{topic_name}
ros2://action/{action_name}
```

Phase 13 validates how a real client interacts with these capabilities.

---

## 5. Client Under Test

The primary real MCP client used during Phase 13 is:

```text
OpenAI Codex CLI
v0.147.0
```

Codex runs from the project directory:

```text
~/projects/robotics/ros2_mcp
```

The model used during the compatibility tests was:

```text
gpt-5.6-sol
```

The compatibility tests focus on the behavior of the MCP client rather than model quality.

---

## 6. Development MCP Registration

The current development server is registered in Codex as:

```text
ros2_mcp_dev
```

This is only the temporary Codex MCP registration name for the development checkout.

The actual project remains:

```text
ros2_mcp
```

The executable remains:

```text
ros2-mcp
```

The development registration starts the server from:

```text
~/projects/robotics/ros2_mcp
```

using the local Python virtual environment and ROS 2 Jazzy environment.

---

## 7. Codex MCP Transport

The Codex development registration uses:

```text
stdio
```

The registered startup command enters the development checkout, activates the project virtual environment, sources ROS 2 Jazzy, and executes:

```text
ros2-mcp
```

The MCP environment includes:

```text
ROS_DOMAIN_ID=30
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

Phase 13 therefore validates the local MCP `stdio` transport.

Remote MCP and HTTP transport are not part of this phase.

---

## 8. Phase 13 Initial Diagnosis

Before the real client compatibility tests started, the development environment was verified.

Initial diagnosis:

```text
Branch dev:             PASS
Working tree clean:     PASS
MCP baseline:           PASS
Codex CLI 0.147.0:      PASS
ros2_mcp_dev in Codex:  PASS
pytest:                  31 passed
Project unchanged:      PASS
```

Claude Code was not installed and was therefore not part of the executed Phase 13 client tests.

---

## 9. Client Compatibility Scope

Phase 13 tests the following client-facing MCP areas:

```text
MCP connection
MCP server discovery
Tool discovery
Tool invocation
Resource Template discovery
Resource reading
Server Instructions
MCP Prompt exposure
structured tool arguments
dry-run behavior
error propagation
safety-preserving behavior
```

The phase deliberately avoids adding functionality merely to satisfy client-specific behavior.

---

## 10. Codex MCP Discovery Test

Codex was started from the development checkout and inspected through its MCP client interface.

The client successfully discovered:

```text
ros2_mcp_dev
```

No MCP server startup error was observed.

The server appeared as an available MCP server in Codex.

Result:

```text
Codex MCP connection: PASS
```

---

## 11. Tool Discovery Test

Codex discovered the complete existing runtime Tool inventory.

The server exposed:

```text
46 Tools
```

Representative discovered Tools included:

```text
get_runtime_health
get_safety_guardrails

list_nodes
list_topics
list_services
list_actions
list_interfaces

node_info
topic_info
service_info
action_info
interface_info

get_parameter
set_parameter
list_parameters

read_topic
read_topic_messages
publish_topic

start_ros_process
stop_ros_process

start_ros_launch
stop_ros_launch

start_bag_recording
stop_bag_recording

start_bag_playback
stop_bag_playback
```

The Tool inventory matched the expected MCP baseline.

Result:

```text
Tool discovery: PASS
```

---

## 12. Resource Discovery Test

Codex also discovered:

```text
0 static resources
9 resource templates
```

The Resource Template inventory matched the Phase 12 implementation:

```text
ros2://runtime/health/{scope}
ros2://runtime/safety/{scope}
ros2://graph/nodes/{scope}
ros2://graph/topics/{scope}
ros2://graph/services/{scope}
ros2://graph/actions/{scope}
ros2://node/{node_name}
ros2://topic/{topic_name}
ros2://action/{action_name}
```

Result:

```text
Resource Template discovery: PASS
```

---

## 13. First Real MCP Tool Invocation

The first direct Codex runtime compatibility test requested the currently available ROS 2 nodes.

Codex was explicitly instructed:

```text
do not inspect repository source code
do not use shell commands to query ROS 2
use the MCP server only
```

Codex selected:

```text
ros2_mcp_dev.list_nodes
```

The returned result was:

```json
[]
```

No public ROS 2 nodes were discovered during that test.

The important compatibility path was:

```text
Codex
    │
    ▼
ros2_mcp_dev
    │
    ▼
list_nodes MCP Tool
    │
    ▼
RuntimeService
    │
    ▼
ROS Adapter
    │
    ▼
ROS 2 Jazzy
```

Result:

```text
Real MCP Tool invocation: PASS
```

---

## 14. Tool Invocation Observation

During the first `list_nodes` compatibility test, Codex issued the same Tool invocation twice.

Conceptually:

```text
list_nodes
list_nodes
```

Both calls completed successfully.

This did not affect correctness.

No server-side workaround was introduced.

The behavior is recorded as a Codex client observation rather than a `ros2_mcp` failure.

---

## 15. Resource Template Client Test

The next compatibility test verified whether Codex could use MCP Resource Templates directly rather than falling back to an MCP Tool.

Codex first discovered the available Resource Templates.

It then attempted to read:

```text
ros2://graph/nodes/local
```

through MCP Resource reading.

The request reached:

```text
resources/read
```

but the server rejected the concrete URI.

The returned error indicated that the Resource could not be created from:

```text
ros2://graph/nodes/local
```

---

## 16. Invalid Scope Diagnosis

The `local` Resource failure was investigated before any implementation change was considered.

The existing Resource definition is:

```text
ros2://graph/nodes/{scope}
```

The current implementation intentionally supports only:

```text
scope=current
```

The Resource handler rejects any other value.

The existing Phase 12 integration tests already verify this behavior.

Valid example:

```text
ros2://graph/nodes/current
```

Invalid example:

```text
ros2://graph/nodes/future
```

Therefore:

```text
ros2://graph/nodes/local
```

was correctly rejected.

The failure was caused by the compatibility test using an unsupported scope.

It was not a Codex Resource protocol failure and not a server implementation defect.

---

## 17. Valid Resource Read Test

The Resource compatibility test was repeated with the supported URI:

```text
ros2://graph/nodes/current
```

Codex first queried the Resource Template inventory.

It then performed a real MCP Resource read.

The operation used:

```text
resources/read
```

against:

```text
ros2://graph/nodes/current
```

The returned MCP Resource content was:

```json
{
  "nodes": []
}
```

Codex correctly interpreted the result.

It did not fall back to:

```text
list_nodes
```

Result:

```text
Resource Template resolution: PASS
resources/read:              PASS
JSON Resource content:       PASS
Tool fallback avoided:       PASS
```

---

## 18. Resource Read Observation

During the successful Resource test, Codex issued two identical Resource read requests.

Both targeted:

```text
ros2://graph/nodes/current
```

Both returned the same correct content.

This did not affect server correctness.

No server-side workaround was introduced.

The duplicate request behavior remains a client-side observation.

---

## 19. Server Instructions Baseline

Phase 10 added server-wide MCP Instructions.

The instructions guide clients to:

```text
use ROS 2 MCP Tools instead of shell commands when appropriate

prefer read-only inspection before changing ROS 2 state

inspect relevant runtime information before state-changing operations

respect server-side safety guardrails

use dry_run=true where supported

only stop resources managed by ros2_mcp

avoid arbitrary shell execution

report real MCP or ROS 2 failures
```

Phase 13 tests whether this capability remains available to real clients.

---

## 20. Codex Server Instructions Visibility Test

Codex was directly asked to summarize the server-wide instructions it received from:

```text
ros2_mcp_dev
```

Codex reported that no server-wide instructions were exposed to the conversational model.

It did not inspect repository files and did not call ROS 2 runtime Tools during this check.

This created an important compatibility question:

```text
Does ros2_mcp fail to expose instructions?

or

Does Codex not expose them to the conversational model?
```

The server was therefore tested independently.

---

## 21. Direct MCP Server Instructions Verification

A direct MCP Python SDK client was connected to the actual `ros2_mcp` server.

The negotiated protocol version was:

```text
2026-07-28
```

The client reported:

```text
discover_result_present: True
```

Supported protocol versions:

```text
2026-07-28
```

The complete Server Instructions were present in the discovery result.

Representative instructions included:

```text
Use the provided ROS 2 MCP tools instead of shell commands whenever an
appropriate ros2_mcp tool exists.

Prefer read-only inspection before changing the ROS 2 runtime.

Respect all safety guardrails exposed by the server.

Use dry_run=true before starting ROS processes, launch files, rosbag
recordings, or rosbag playback when validating an operation and when
dry-run is supported.

Do not construct or request arbitrary shell execution through ros2_mcp.

When an MCP or ROS 2 operation fails, report the actual failure instead
of hiding it or silently replacing it with a different operation.
```

This independently verified the server implementation.

Result:

```text
Server Instructions present: PASS
MCP discovery result:        PASS
Protocol 2026-07-28:         PASS
```

---

## 22. Server Instructions Compatibility Boundary

The direct MCP SDK test proves that `ros2_mcp` exposes the Server Instructions correctly.

Codex 0.147.0 did not expose those instructions directly to the conversational model when explicitly asked to reproduce them.

Therefore the Phase 13 boundary is:

```text
ros2_mcp Server Instructions:
PASS

Codex direct instruction visibility:
LIMITED / NOT EXPOSED
```

No server implementation was changed to work around this client behavior.

---

## 23. Behavioral Server Instructions Test

A second Codex test checked behavior rather than direct instruction visibility.

Codex was asked to inspect the current ROS 2 runtime and choose the safest appropriate operation itself.

It was not told which Tool to use.

Codex selected:

```text
ros2_mcp_dev.get_runtime_health
```

The operation is read-only.

The returned runtime summary was:

```text
health:       OK
nodes:        1
topics:       2
services:     7
diagnostics:  0
```

ROS log summary:

```text
warn:   0
error:  0
fatal:  0
```

Codex explained that it selected `get_runtime_health` because it provides a broad runtime overview without changing ROS state.

This behavior is consistent with the Phase 10 Server Instructions.

---

## 24. Server Instructions Result

The combined result is:

```text
Server exposes Instructions:          PASS
Direct MCP SDK reads Instructions:    PASS
Codex direct model visibility:        LIMITED
Codex safe read-only behavior:        PASS
```

The behavioral test alone does not prove that the Server Instructions caused Codex to select the read-only operation.

However, the observed behavior is consistent with those instructions.

Phase 13 therefore records:

```text
SERVER INSTRUCTIONS:
PASS WITH CODEX VISIBILITY LIMITATION
```

---

## 25. MCP Prompt Compatibility Test

Phase 11 provides:

```text
6 MCP Prompts
```

The Prompts are already validated through the permanent MCP integration tests.

Phase 13 checked whether Codex 0.147.0 exposes those MCP Prompts to the client interaction layer.

Codex was instructed to check only the MCP client capability.

It was explicitly instructed not to:

```text
inspect repository files
use shell commands
call ROS 2 runtime Tools
```

Codex reported that no MCP Prompt-listing interface or Prompt endpoint was exposed for:

```text
ros2_mcp_dev
```

Therefore the Prompt names could not be enumerated through that Codex client interface.

---

## 26. MCP Prompt Compatibility Boundary

The server-side Prompt implementation remains verified by the existing MCP tests.

The Phase 13 Codex result is:

```text
ros2_mcp MCP Prompts:
PASS

Codex 0.147.0 Prompt exposure:
NOT EXPOSED
```

This is treated as a client capability boundary.

No server workaround was introduced.

---

## 27. Dry-Run Compatibility Test

Phase 13 also validates a Tool path that represents a potentially state-changing operation.

The selected Tool was:

```text
start_ros_process
```

To prevent an actual process from being started, Codex was instructed to use:

```text
dry_run=true
```

The harmless validation target was:

```text
package:
demo_nodes_cpp

executable:
talker
```

---

## 28. Dry-Run Tool Invocation

Codex invoked:

```text
ros2_mcp_dev.start_ros_process
```

with:

```json
{
  "package_name": "demo_nodes_cpp",
  "executable": "talker",
  "arguments": [],
  "dry_run": true
}
```

The server returned:

```json
{
  "dry_run": true,
  "package": "demo_nodes_cpp",
  "executable": "talker",
  "arguments": [],
  "resolved_executable": "/opt/ros/jazzy/lib/demo_nodes_cpp/talker"
}
```

The executable was successfully resolved to:

```text
/opt/ros/jazzy/lib/demo_nodes_cpp/talker
```

No process was started.

---

## 29. Dry-Run Compatibility Result

The dry-run test verifies:

```text
structured Tool arguments:      PASS
package resolution:             PASS
executable resolution:          PASS
dry-run handling:               PASS
no real process start:          PASS
Codex Tool invocation:          PASS
```

This confirms that Codex can use a state-changing Tool schema while preserving the server's explicit validation mechanism.

---

## 30. Error Propagation Test

Phase 13 also verifies that MCP and ROS 2 failures are reported rather than silently replaced with another operation.

Codex was instructed to validate an intentionally nonexistent ROS 2 target.

The requested package was:

```text
ros2_mcp_phase13_nonexistent_package
```

The requested executable was:

```text
nonexistent_executable
```

The request again used:

```text
dry_run=true
```

Codex was explicitly instructed not to try another package if the operation failed.

---

## 31. Error Tool Invocation

Codex invoked:

```text
ros2_mcp_dev.start_ros_process
```

with:

```json
{
  "package_name": "ros2_mcp_phase13_nonexistent_package",
  "executable": "nonexistent_executable",
  "dry_run": true
}
```

The server rejected the target.

The reported error was:

```text
Error executing tool start_ros_process: ros2_mcp_phase13_nonexistent_package
```

The MCP result was marked as:

```text
isError: true
```

---

## 32. Error Handling Behavior

After the expected failure, Codex did not:

```text
try another ROS package
use a shell command
inspect repository source code
start a process
hide the server error
replace the operation with another Tool
```

Instead, Codex reported the actual server error.

Result:

```text
MCP error propagation:          PASS
No fallback operation:          PASS
No shell fallback:              PASS
No process start:               PASS
Original failure preserved:     PASS
```

---

## 33. Safety Behavior Across Client Tests

The real Codex compatibility tests demonstrated safety-preserving behavior across multiple scenarios.

Observed behavior:

```text
read-only inspection used for runtime overview
MCP Tools preferred over shell commands
Resource reads used directly when requested
dry_run=true respected
invalid targets rejected
server errors preserved
no fallback package attempted
no arbitrary shell execution used
```

These behaviors are compatible with the existing `ros2_mcp` safety architecture.

The server-side guardrails remain authoritative.

---

## 34. No New ROS 2 Functionality

Phase 13 intentionally adds no new ROS 2 runtime functionality.

The following areas remain unchanged:

```text
ROS Adapter
RuntimeService
ROS graph discovery
topic operations
service operations
action operations
parameter operations
process management
launch management
rosbag management
QoS handling
diagnostics
rosout handling
safety guardrails
```

The purpose of Phase 13 is compatibility validation only.

---

## 35. No Client-Specific Server Workarounds

The compatibility tests exposed several Codex-specific observations:

```text
duplicate Tool calls
duplicate Resource reads
Server Instructions not directly visible to the conversational model
MCP Prompts not exposed through the Codex client interface
```

No workaround was added to `ros2_mcp` for these behaviors.

This preserves the MCP server architecture as client-neutral.

---

## 36. Codex Compatibility Matrix

The Phase 13 Codex results are:

```text
Codex CLI 0.147.0

MCP connection:                    PASS
MCP server discovery:              PASS
Tool discovery:                    PASS
46 Tools visible:                  PASS
Read-only Tool invocation:         PASS

Resource Template discovery:       PASS
9 Resource Templates visible:      PASS
resources/read:                    PASS
Resource JSON content:             PASS

Server Instructions on server:     PASS
Direct SDK Instructions read:      PASS
Codex direct Instructions view:    LIMITED
Codex safe behavior:               PASS

MCP Prompts on server:             PASS
Codex Prompt exposure:             NOT EXPOSED

Structured Tool arguments:         PASS
Dry-run Tool execution:            PASS
Executable resolution:             PASS
Error propagation:                 PASS
No shell fallback:                 PASS
No unsafe fallback:                PASS
```

---

## 37. Client Observations

The following observations are recorded for Codex CLI 0.147.0:

```text
1. Some read-only Tool calls may be issued more than once.

2. Some Resource reads may be issued more than once.

3. Server Instructions are present on the MCP server but were not directly
   exposed when the conversational model was asked to reproduce them.

4. MCP Prompts are present on the server but were not exposed through the
   tested Codex client interface.
```

These observations did not require a change to `ros2_mcp`.

---

## 38. Compatibility Interpretation

Phase 13 distinguishes between:

```text
server capability
```

and:

```text
client exposure
```

A capability can be correctly implemented by `ros2_mcp` even when a particular client does not expose that capability to its conversational interface.

This distinction is important for:

```text
Server Instructions
MCP Prompts
```

The server remains the authoritative implementation boundary.

---

## 39. Existing MCP Regression Tests

The permanent automated MCP tests remain responsible for validating protocol and server behavior independently from Codex.

The test suite covers the previous implementation phases including:

```text
Phase 9
MCP 2026-07-28 protocol compliance

Phase 10
Server Instructions

Phase 11
MCP Prompts

Phase 12
MCP Resources
```

Phase 13 does not replace these automated tests.

It adds real-client compatibility evidence.

---

## 40. Final Phase 13 Verification

After completing the real Codex compatibility tests, the complete development environment was verified again.

Branch:

```text
dev
```

Working tree before the final test suite:

```text
clean
```

MCP SDK:

```text
2.0.0
```

Codex CLI:

```text
0.147.0
```

Codex MCP registration:

```text
ros2_mcp_dev
```

Registration state:

```text
enabled
```

---

## 41. Final Automated Test Suite

The complete project test suite was executed after the real client compatibility tests.

Result:

```text
............................... [100%]

31 passed in 6.74s
```

Summary:

```text
31 passed
```

No regression was detected.

---

## 42. Final Git State

The Git working tree was checked before and after the final automated test suite.

Before:

```text
clean
```

After:

```text
clean
```

The client compatibility tests therefore did not modify project files.

---

## 43. Current MCP Inventory

At the end of Phase 13:

```text
MCP protocol baseline:
2026-07-28

MCP SDK:
2.0.0

Server Instructions:
enabled

MCP Tools:
46

MCP Prompts:
6

Static MCP Resources:
0

MCP Resource Templates:
9
```

The server capability inventory remains unchanged from Phase 12.

---

## 44. Phase 13 Quality Results

The Phase 13 compatibility verification produced:

```text
Development branch:              PASS
Clean initial working tree:      PASS
MCP protocol baseline:           PASS
MCP SDK 2.0.0:                   PASS
Codex CLI 0.147.0:               PASS
ros2_mcp_dev registration:       PASS

MCP connection:                  PASS
Tool discovery:                  PASS
Real Tool invocation:            PASS

Resource Template discovery:     PASS
Resource read:                   PASS
Resource JSON result:            PASS

Server Instructions server-side: PASS
Instructions direct SDK read:    PASS
Codex Instructions visibility:   LIMITED
Codex safe behavior:             PASS

MCP Prompts server-side:         PASS
Codex Prompt exposure:           NOT EXPOSED

Dry-run validation:              PASS
Structured arguments:            PASS
Executable resolution:           PASS

Error propagation:               PASS
No unsafe fallback:              PASS
No shell fallback:               PASS

Full pytest:                     PASS
Working tree after tests:        CLEAN
```

---

## 45. What Phase 13 Does Not Implement

Phase 13 intentionally does not implement:

```text
new ROS 2 runtime Tools
new MCP Prompts
new MCP Resources
new Server Instructions
Remote MCP transport
HTTP transport
OAuth
remote authentication
Windows remote client access
macOS remote client access
multi-client transport infrastructure
```

Those are outside the scope of Client Compatibility Tests.

---

## 46. Claude Code Status

Claude Code was not installed in the Phase 13 development environment.

Therefore no real Claude Code compatibility test was executed.

Phase 13 does not claim Claude Code compatibility.

The verified real external client is:

```text
OpenAI Codex CLI 0.147.0
```

---

## 47. Current Version 2 Development Sequence

The fixed Version 2 development sequence now stands at:

```text
Phase 9
MCP 2026-07-28 Compliance
        │
        │ PASS
        ▼
Phase 10
Server Instructions
        │
        │ PASS
        ▼
Phase 11
MCP Prompts
        │
        │ PASS
        ▼
Phase 12
MCP Resources
        │
        │ PASS
        ▼
Phase 13
Client Compatibility Tests
        │
        │ TESTED
        ▼
Phase 14
Remote MCP / HTTP
```

No additional phase is inserted between Phase 13 and Phase 14.

---

## 48. Phase 14 Boundary

The next phase is:

```text
Phase 14
Remote MCP / HTTP
```

Phase 14 is responsible for transport and remote-access concerns.

Phase 13 deliberately remains focused on client compatibility against the existing local `stdio` server.

The transition is therefore:

```text
Phase 13
Real client compatibility
        │
        ▼
Phase 14
Remote MCP / HTTP
```

---

## 49. Development Registration Naming

The actual project remains:

```text
ros2_mcp
```

Python package:

```text
ros2_mcp
```

Executable:

```text
ros2-mcp
```

Temporary Codex development registration:

```text
ros2_mcp_dev
```

The development registration name must not be confused with the project name.

---

## 50. Phase 13 Final Status

Current verified development state:

```text
Branch:
dev

MCP protocol:
2026-07-28

MCP SDK:
2.0.0

Codex CLI:
0.147.0

Codex development registration:
ros2_mcp_dev

Server Instructions:
enabled

MCP Tools:
46

MCP Prompts:
6

Static MCP Resources:
0

MCP Resource Templates:
9

Codex MCP connection:
PASS

Codex Tool discovery:
PASS

Codex real Tool invocation:
PASS

Codex Resource discovery:
PASS

Codex resources/read:
PASS

Server Instructions server-side:
PASS

Codex direct Instructions visibility:
LIMITED

Codex safe read-only behavior:
PASS

MCP Prompts server-side:
PASS

Codex Prompt exposure:
NOT EXPOSED

Dry-run Tool validation:
PASS

Error propagation:
PASS

No shell fallback:
PASS

No unsafe fallback:
PASS

Complete test suite:
31 passed

Final working tree:
clean
```

## Phase 13 Result

```text
PHASE 13 CLIENT COMPATIBILITY TESTS: PASS
```

Phase 13 validates `ros2_mcp` against OpenAI Codex CLI 0.147.0 using the MCP `2026-07-28` protocol baseline and MCP Python SDK 2.0.0.

The real client successfully discovers and invokes MCP Tools, discovers and reads Resource Templates, passes structured arguments, respects dry-run validation, and preserves MCP server errors.

Server Instructions remain correctly exposed by `ros2_mcp`, while direct instruction visibility and MCP Prompt exposure show Codex 0.147.0 client-side limitations.

No new ROS 2 functionality and no client-specific server workaround were introduced during Phase 13.

The next fixed development phase is:

```text
Phase 14 – Remote MCP / HTTP
```
