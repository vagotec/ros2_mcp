# Phase 11 – Modular MCP Prompts

## 1. Goal

Phase 11 adds native MCP Prompts to `ros2_mcp`.

The prompts provide reusable ROS 2 diagnostic and inspection workflows that MCP clients can expose directly to users.

Phase 11 builds on the MCP foundation established by the previous phases:

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
```

The existing ROS 2 runtime implementation remains unchanged.

Phase 11 does not add new ROS 2 runtime operations.

Instead, it provides structured workflows that guide an MCP client in using the existing ROS 2 MCP tools.

---

## 2. Development Branch

Phase 11 is developed on:

```text
dev
```

The stable Version 1 implementation remains on:

```text
main
```

Phase 11 will remain on `dev` together with the other Version 2 MCP extensions until the complete development sequence has been tested and is ready to merge.

---

## 3. MCP Protocol Baseline

The required MCP protocol baseline remains:

```text
2026-07-28
```

The installed MCP packages used during Phase 11 development are:

```text
mcp:       2.0.0
mcp-types: 2.0.0
```

Phase 11 was implemented without changing the protocol baseline established by Phase 9.

---

## 4. Why MCP Prompts Are Useful

The existing `ros2_mcp` server already exposes individual MCP tools.

Examples include operations for:

```text
nodes
topics
services
actions
parameters
diagnostics
rosout
QoS
runtime health
safety
processes
launches
rosbag
```

A tool represents an individual operation.

A prompt represents a reusable workflow describing how several tools can be combined to solve a higher-level task.

For example:

```text
User:
"Check whether my ROS 2 system is healthy."

        │
        ▼

MCP Prompt:
ros_health_check

        │
        ▼

LLM / MCP Client

        │
        ├── list nodes
        ├── list topics
        ├── inspect diagnostics
        ├── inspect rosout
        └── inspect runtime health

        │
        ▼

Health analysis
```

The prompt therefore does not replace the existing MCP tools.

It provides structured guidance for using them.

---

## 5. Important Architectural Principle

Phase 11 follows the same modular architecture principle already used by the ROS adapter implementation.

The ROS adapter architecture separates a central integration layer from specialized modules.

Phase 11 applies the same principle to MCP Prompts.

Instead of placing all prompt implementations inside one large file, the architecture uses:

```text
prompts.py
    │
    └── prompt/
        ├── ros_health_check.py
        ├── diagnose_node.py
        ├── diagnose_topic.py
        ├── diagnose_action.py
        ├── inspect_runtime_logs.py
        └── safe_runtime_review.py
```

The central module handles registration.

The specialized modules contain the individual workflow definitions.

---

## 6. Phase 11 Project Structure

The MCP portion of the project now contains:

```text
src/ros2_mcp/mcp/
│
├── __init__.py
│
├── instructions.py
│
├── runtime_tools.py
│
├── prompts.py
│
└── prompt/
    ├── __init__.py
    ├── ros_health_check.py
    ├── diagnose_node.py
    ├── diagnose_topic.py
    ├── diagnose_action.py
    ├── inspect_runtime_logs.py
    └── safe_runtime_review.py
```

Responsibilities:

```text
instructions.py
    │
    └── MCP Server Instructions

runtime_tools.py
    │
    └── MCP ROS 2 tools

prompts.py
    │
    └── MCP Prompt registration

prompt/
    │
    └── Individual ROS 2 workflows
```

---

## 7. Central Prompt Registration

The central prompt registration module is:

```text
src/ros2_mcp/mcp/prompts.py
```

Its responsibility is to register the available prompt modules with the MCP server.

Conceptually:

```text
server.py
    │
    ▼
register_prompts(server)
    │
    ▼
prompts.py
    │
    ├── ros_health_check
    ├── diagnose_node
    ├── diagnose_topic
    ├── diagnose_action
    ├── inspect_runtime_logs
    └── safe_runtime_review
```

This keeps `server.py` small and prevents prompt-specific workflow content from being placed directly inside the MCP server bootstrap code.

---

## 8. Server Integration

The MCP server now performs three major MCP configuration operations:

```text
create MCPServer
        │
        ├── Server Instructions
        │
        ├── register Runtime Tools
        │
        └── register Prompts
```

Conceptually:

```python
server = MCPServer(
    name="ros2-mcp",
    instructions=SERVER_INSTRUCTIONS,
    lifespan=app_lifespan,
)

register_runtime_tools(server)
register_prompts(server)
```

The existing runtime tool registration remains separate from prompt registration.

---

## 9. Prompt Inventory

Phase 11 introduces:

```text
6 MCP Prompts
```

The prompt inventory is:

```text
ros_health_check
diagnose_node
diagnose_topic
diagnose_action
inspect_runtime_logs
safe_runtime_review
```

These prompts are intentionally generic ROS 2 workflows.

They do not contain robot-specific application logic.

---

## 10. ros_health_check

Module:

```text
src/ros2_mcp/mcp/prompt/ros_health_check.py
```

MCP Prompt:

```text
ros_health_check
```

Title:

```text
ROS 2 Health Check
```

Arguments:

```text
none
```

Purpose:

Perform a read-only inspection of the overall ROS 2 runtime.

The workflow guides the MCP client to inspect:

```text
nodes
topics
diagnostics
/rosout
runtime health
```

The result should summarize:

```text
runtime structure
warnings
errors
diagnostic problems
suspicious missing components
overall runtime health
```

The workflow explicitly avoids runtime modification.

---

## 11. diagnose_node

Module:

```text
src/ros2_mcp/mcp/prompt/diagnose_node.py
```

MCP Prompt:

```text
diagnose_node
```

Title:

```text
Diagnose ROS 2 Node
```

Required argument:

```text
node_name
```

Example:

```text
/camera
```

The workflow guides the MCP client to inspect:

```text
node information
topics
services
actions
parameters
diagnostics
/rosout
runtime health
```

The purpose is to correlate several pieces of ROS graph and runtime information around one specific node.

---

## 12. diagnose_topic

Module:

```text
src/ros2_mcp/mcp/prompt/diagnose_topic.py
```

MCP Prompt:

```text
diagnose_topic
```

Title:

```text
Diagnose ROS 2 Topic
```

Required argument:

```text
topic_name
```

Example:

```text
/chatter
```

The workflow guides the MCP client to inspect:

```text
topic information
message interface type
publishers
subscribers
endpoint QoS
recommended QoS
recent messages
related nodes
```

The prompt is intended to help diagnose common ROS 2 communication problems such as:

```text
missing publishers
missing subscribers
unexpected message types
QoS incompatibilities
missing data
```

The workflow is read-only and does not publish messages.

---

## 13. diagnose_action

Module:

```text
src/ros2_mcp/mcp/prompt/diagnose_action.py
```

MCP Prompt:

```text
diagnose_action
```

Title:

```text
Diagnose ROS 2 Action
```

Required argument:

```text
action_name
```

Example:

```text
/navigate_to_pose
```

The workflow guides the MCP client to inspect:

```text
action information
action interface
action servers
action clients
related nodes
diagnostics
/rosout
action status information
```

The prompt is diagnostic only.

It explicitly instructs the client not to:

```text
send goals
cancel goals
```

---

## 14. inspect_runtime_logs

Module:

```text
src/ros2_mcp/mcp/prompt/inspect_runtime_logs.py
```

MCP Prompt:

```text
inspect_runtime_logs
```

Title:

```text
Inspect ROS 2 Runtime Logs
```

Arguments:

```text
none
```

The workflow guides the client to inspect `/rosout` and focus on:

```text
WARN
ERROR
FATAL
```

It also encourages correlation with:

```text
affected nodes
diagnostics
runtime health
```

The expected result includes:

```text
important log messages
affected nodes
repeated warnings
repeated errors
likely causes
recommended diagnostic steps
```

---

## 15. safe_runtime_review

Module:

```text
src/ros2_mcp/mcp/prompt/safe_runtime_review.py
```

MCP Prompt:

```text
safe_runtime_review
```

Title:

```text
Safe ROS 2 Runtime Review
```

Arguments:

```text
none
```

This workflow combines runtime inspection with the existing `ros2_mcp` safety model.

It guides the MCP client to inspect:

```text
runtime health
safety guardrails
nodes
diagnostics
/rosout
managed processes
managed launches
managed rosbag operations
```

The workflow reports:

```text
runtime health
active safety restrictions
protected resources
runtime limits
managed resources
warnings
errors
operations requiring dry-run validation
```

It explicitly instructs the client not to bypass safety controls.

---

## 16. Static and Parameterized Prompts

Phase 11 supports both static and parameterized MCP Prompts.

### Static prompts

Examples:

```text
ros_health_check
inspect_runtime_logs
safe_runtime_review
```

These prompts require no arguments.

### Parameterized prompts

Examples:

```text
diagnose_node
diagnose_topic
diagnose_action
```

They require a target ROS entity.

For example:

```text
diagnose_topic
    │
    └── topic_name = "/chatter"
```

The MCP SDK exposes the function parameter automatically as a prompt argument.

The Phase 11 diagnosis verified that the argument is marked as required.

---

## 17. MCP Prompt Discovery

An MCP client can discover the prompts using the MCP prompt discovery operation.

During Phase 11 verification:

```text
Protocol: 2026-07-28
Tool count: 46
Prompt count: 6
```

The discovered prompts were:

```text
ros_health_check
diagnose_node
diagnose_topic
diagnose_action
inspect_runtime_logs
safe_runtime_review
```

The parameterized prompts exposed the expected arguments:

```text
diagnose_node
    node_name

diagnose_topic
    topic_name

diagnose_action
    action_name
```

---

## 18. MCP Prompt Rendering

Phase 11 also verifies actual prompt rendering.

For example:

```text
diagnose_topic
```

with:

```text
topic_name = /chatter
```

produces a rendered MCP prompt containing:

```text
/chatter
```

and workflow instructions covering:

```text
topic information
message type
publishers
subscribers
QoS
recent messages
```

This confirms that prompt registration alone is not being tested.

The client performs a real MCP `get_prompt` operation.

---

## 19. Prompts Do Not Execute ROS Operations Directly

A central design decision is:

```text
MCP Prompt
    ≠
ROS operation
```

A prompt returns instructions to the MCP client.

It does not directly call `rclpy`, the ROS adapter, or the runtime service.

The architecture remains:

```text
MCP Prompt
    │
    ▼
MCP Client / LLM
    │
    ▼
MCP Tools
    │
    ▼
Application Runtime Service
    │
    ▼
ROS Adapter
    │
    ▼
ROS 2 Jazzy
```

This preserves the existing separation between:

```text
workflow guidance
```

and:

```text
runtime execution
```

---

## 20. Relationship Between Server Instructions and Prompts

Phase 10 and Phase 11 solve different problems.

### Server Instructions

Server Instructions provide general behavior guidance for the complete `ros2_mcp` server.

They describe how the client should generally interact with the server and its safety model.

### MCP Prompts

Prompts provide specific reusable workflows.

For example:

```text
Server Instructions
        │
        └── General ros2_mcp behavior

MCP Prompts
        │
        ├── Diagnose this node
        ├── Diagnose this topic
        ├── Check runtime health
        └── Review runtime safety
```

Both mechanisms complement the existing MCP tools.

---

## 21. Relationship Between Prompts and Tools

After Phase 11, the server exposes:

```text
46 MCP Tools
6 MCP Prompts
```

These are separate MCP capabilities.

Prompts do not reduce or replace the tool inventory.

Phase 11 permanently verifies that both capabilities coexist.

```text
ros2_mcp
│
├── Server Instructions
│
├── 46 MCP Tools
│
└── 6 MCP Prompts
```

---

## 22. Safety Design

The Phase 11 prompts follow a read-only-first design.

Diagnostic prompts explicitly avoid state-changing operations unless a user separately requests such an operation.

Examples include:

```text
Do not publish to the topic.

Do not send an action goal.

Do not cancel an action goal.

Do not start or stop processes.

Do not bypass safety guardrails.
```

This complements the runtime safety enforcement already implemented by the server.

Prompt instructions are guidance.

The existing runtime safety mechanisms remain the enforcement layer.

---

## 23. Phase 11 Integration Tests

The permanent Phase 11 integration tests are located at:

```text
tests/integration/test_mcp_prompts.py
```

The file contains three tests:

```text
test_prompt_inventory
test_prompt_rendering
test_prompts_and_tools_coexist
```

---

## 24. Prompt Inventory Test

The prompt inventory test verifies that exactly the expected Phase 11 prompts are exposed:

```text
ros_health_check
diagnose_node
diagnose_topic
diagnose_action
inspect_runtime_logs
safe_runtime_review
```

It also verifies the argument contracts.

Static prompts must expose no arguments.

Parameterized prompts must expose:

```text
node_name
topic_name
action_name
```

and those arguments must be required.

---

## 25. Prompt Rendering Test

The rendering test performs real MCP `get_prompt` operations.

It verifies representative static and parameterized prompts.

Examples include:

```text
ros_health_check
diagnose_topic("/chatter")
diagnose_node("/camera")
diagnose_action("/navigate_to_pose")
```

The test confirms that the supplied ROS entity names appear in the rendered prompt content.

---

## 26. Tool Coexistence Test

Phase 11 verifies that adding MCP Prompts does not change the existing MCP tool inventory.

Expected state:

```text
MCP tools:   46
MCP prompts: 6
```

This protects the existing Version 1 ROS 2 functionality from accidental regression while new MCP capabilities are added.

---

## 27. Phase 9 Regression

The permanent Phase 9 MCP protocol tests remain green after the Phase 11 implementation.

Result:

```text
2 passed
```

This verifies that adding MCP Prompts did not break the required:

```text
MCP 2026-07-28
```

protocol baseline.

---

## 28. Phase 10 Regression

The permanent Phase 10 Server Instructions tests remain green after the Phase 11 implementation.

Result:

```text
2 passed
```

This verifies that MCP Prompts and Server Instructions coexist correctly.

---

## 29. Full Regression Suite

Before Phase 11:

```text
24 tests
```

Phase 11 adds:

```text
3 tests
```

The complete regression result is:

```text
27 passed
```

Test collection result:

```text
27 tests collected
```

---

## 30. Phase 11 Quality Results

The implementation verification produced:

```text
Prompt inventory:    PASS
Phase 11 tests:      PASS
Phase 10 regression: PASS
Phase 9 regression:  PASS
Python syntax:       PASS
Full pytest:         PASS
Test collection:     PASS
Diff quality:        PASS
```

Dedicated Phase 11 result:

```text
3 passed
```

Complete project result:

```text
27 passed
```

---

## 31. What Phase 11 Does Not Implement

Phase 11 is intentionally limited to MCP Prompts.

It does not implement:

```text
MCP Resources
Remote MCP / HTTP
Windows remote access
macOS remote access
multi-client compatibility tests
```

It also does not add new ROS 2 runtime tools.

Those capabilities belong to later phases.

---

## 32. Current MCP Architecture

After Phase 11, the MCP side of the architecture is:

```text
MCP Client
    │
    ▼
ros2_mcp
    │
    ├── Server Instructions
    │
    ├── MCP Prompts
    │       │
    │       ├── ros_health_check
    │       ├── diagnose_node
    │       ├── diagnose_topic
    │       ├── diagnose_action
    │       ├── inspect_runtime_logs
    │       └── safe_runtime_review
    │
    └── MCP Tools
            │
            ▼
    Application Runtime Service
            │
            ▼
       ROS Adapter
            │
            ▼
      ROS 2 Jazzy
```

---

## 33. Current Development Sequence

The Version 2 development sequence now stands at:

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
        │ IMPLEMENTED / TESTED
        ▼
Phase 12
MCP Resources
        │
        ▼
Client Compatibility Tests
        │
        ▼
Remote MCP / HTTP
```

Phase 11 must be committed to `dev` before development proceeds to Phase 12.

---

## 34. Future Extensibility

The modular prompt architecture allows additional prompt families to be introduced without turning `prompts.py` into a large monolithic implementation.

For example, future projects could extend the structure with specialized workflows:

```text
prompt/
│
├── ros_health_check.py
├── diagnose_node.py
├── diagnose_topic.py
├── diagnose_action.py
├── inspect_runtime_logs.py
├── safe_runtime_review.py
│
├── ros2_control/
│   └── ...
│
├── moveit/
│   └── ...
│
└── nav2/
    └── ...
```

The central registration layer can remain responsible for composing the available prompt modules.

This follows the same modularity principle used elsewhere in `ros2_mcp`.

---

## 35. Phase 11 Final Status

Current verified development state:

```text
Branch: dev

MCP protocol: 2026-07-28

Server Instructions: enabled

MCP tools:   46
MCP prompts: 6

Prompt discovery: PASS
Static prompts: PASS
Parameterized prompts: PASS
Prompt rendering: PASS
Prompt/tool coexistence: PASS

Phase 9 regression: PASS
Phase 10 regression: PASS
Phase 11 tests: PASS

Python syntax: PASS
Full regression: PASS
Diff quality: PASS

Complete test suite:
27 passed
```

## Phase 11 Result

```text
PHASE 11 MODULAR MCP PROMPTS: PASS
```

Phase 11 adds a modular MCP Prompt architecture to `ros2_mcp` while preserving the existing ROS 2 runtime architecture, the 46 MCP tools, Server Instructions, safety controls, and the MCP `2026-07-28` protocol baseline.
