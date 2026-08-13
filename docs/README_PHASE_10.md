# Phase 10 – MCP Server Instructions

## 1. Goal

Phase 10 adds **MCP Server Instructions** to `ros2_mcp`.

Server Instructions provide operational guidance to MCP clients and the language models using the server.

They describe how the existing ROS 2 MCP tools should be used safely and predictably.

Phase 10 does **not** add new ROS 2 runtime functionality.

The existing:

```text
46 MCP tools
```

remain unchanged.

---

## 2. Development Branch

Phase 10 is developed on:

```text
dev
```

The stable Version 1 implementation remains on:

```text
main
```

The Phase 10 changes are developed and tested on `dev` before the development branch is eventually merged into `main`.

---

## 3. MCP Protocol Baseline

Phase 10 continues to use the MCP protocol baseline established by Phase 9:

```text
2026-07-28
```

Phase 9 introduced permanent regression tests for this protocol baseline.

Phase 10 must not break those tests.

Verified result:

```text
MCP protocol: 2026-07-28
Phase 9 regression tests: PASS
```

---

## 4. What Are MCP Server Instructions?

MCP Server Instructions are guidance provided by the MCP server during initialization.

They help an MCP client and its language model understand how the server should be used.

For `ros2_mcp`, the instructions describe operational principles such as:

```text
Prefer ROS 2 MCP tools over shell commands
Prefer read-only inspection before changing runtime state
Respect server safety guardrails
Use dry-run where supported
Only stop resources managed by ros2_mcp
Do not request arbitrary shell execution
Report actual MCP or ROS 2 failures
```

Server Instructions guide the client.

They do **not** replace server-side security or safety enforcement.

---

## 5. Architecture

Phase 10 extends the MCP layer without changing the ROS 2 runtime architecture.

```text
MCP Client / LLM
        │
        │ MCP initialize
        │
        │ receives Server Instructions
        ▼
+-------------------------------+
|          ros2_mcp             |
|                               |
|  MCP Server Instructions      |
|             │                 |
|             ▼                 |
|        MCP Tools              |
|        46 tools               |
+---------------+---------------+
                │
                ▼
       Application Runtime
                │
                ▼
       ROS Adapter Interface
                │
                ▼
       ROS 2 Jazzy Adapter
                │
                ▼
       Safety Guardrails
                │
                ▼
           ROS 2 Jazzy
```

The instructions operate at the MCP guidance layer.

The safety implementation remains authoritative at the server/runtime layer.

---

## 6. Instructions Module

The Server Instructions are defined in:

```text
src/ros2_mcp/mcp/instructions.py
```

This keeps MCP guidance separate from the server bootstrap code.

The module exposes:

```python
SERVER_INSTRUCTIONS
```

The instructions are therefore maintained independently from:

```text
server lifecycle
ROS adapter creation
runtime service creation
tool registration
configuration loading
```

This follows the existing modular architecture of `ros2_mcp`.

---

## 7. Server Integration

The server imports:

```python
from ros2_mcp.mcp.instructions import SERVER_INSTRUCTIONS
```

The instructions are passed directly to the MCP server:

```python
server = MCPServer(
    name="ros2-mcp",
    instructions=SERVER_INSTRUCTIONS,
    lifespan=app_lifespan,
)
```

Tool registration remains unchanged:

```python
register_runtime_tools(server)
```

This means Phase 10 extends the MCP initialization metadata without changing the existing runtime tool architecture.

---

## 8. Operational Guidance

The Phase 10 Server Instructions establish several rules for MCP clients.

### 8.1 Prefer ROS 2 MCP Tools

Clients are instructed to use the structured `ros2_mcp` tools instead of shell commands whenever an appropriate MCP tool exists.

This preserves the controlled ROS 2 interface provided by the project.

The intended architecture is:

```text
LLM / MCP Client
        │
        ▼
structured MCP tool
        │
        ▼
ros2_mcp
        │
        ▼
ROS 2
```

instead of:

```text
LLM
 │
 ▼
arbitrary shell command
 │
 ▼
ROS 2
```

---

## 9. Inspect Before Changing

Clients are instructed to prefer read-only inspection before changing the runtime.

Relevant information can include:

```text
nodes
topics
services
actions
parameters
diagnostics
runtime health
QoS
```

This encourages a workflow such as:

```text
inspect
   │
   ▼
understand current ROS state
   │
   ▼
validate intended operation
   │
   ▼
perform controlled change
```

This is especially useful for autonomous or semi-autonomous MCP clients because they should understand the current ROS 2 environment before performing state-changing operations.

---

## 10. Respect Safety Guardrails

Clients are explicitly instructed not to bypass server-side safety controls.

Examples include restrictions around:

```text
protected topics
protected services
protected parameters
protected actions
package restrictions
launch restrictions
managed resources
runtime limits
```

These instructions describe expected client behavior.

Actual enforcement remains inside `ros2_mcp`.

The client therefore receives guidance, while the server remains responsible for enforcement.

---

## 11. Dry-Run Guidance

The Server Instructions tell clients to use:

```text
dry_run=true
```

when validating supported state-changing operations.

Relevant operations can include:

```text
starting ROS processes
starting ROS launch files
starting rosbag recording
starting rosbag playback
```

Dry-run allows an operation to be validated without immediately performing the runtime action when the corresponding tool supports dry-run.

The preferred workflow becomes:

```text
request
   │
   ▼
dry-run validation
   │
   ▼
result inspection
   │
   ▼
real operation
```

---

## 12. Managed Resource Guidance

The instructions state that clients should only stop resources managed by `ros2_mcp`.

Examples include:

```text
managed processes
managed launch sessions
managed rosbag recordings
managed rosbag playback sessions
```

This guidance matches the existing managed-resource safety model.

The MCP client should not assume that every process or ROS resource visible on the host belongs to `ros2_mcp`.

---

## 13. Arbitrary Shell Execution

The Server Instructions explicitly state that clients must not construct or request arbitrary shell execution through `ros2_mcp`.

The project provides structured ROS 2 operations instead of a generic shell interface.

The intended model is:

```text
MCP Tool
   │
   ▼
validated structured arguments
   │
   ▼
ROS 2 operation
```

and not:

```text
arbitrary command string
   │
   ▼
shell
```

The server-side safety implementation remains responsible for enforcing the actual restrictions.

---

## 14. Error Handling Guidance

The instructions require MCP and ROS 2 failures to be reported as actual failures.

A client should not silently replace a failed operation with an unrelated operation.

The intended behavior is:

```text
requested operation
        │
        ▼
      failure
        │
        ▼
report actual MCP / ROS 2 failure
```

rather than:

```text
requested operation
        │
        ▼
      failure
        │
        ▼
silently perform something different
```

This makes client behavior more predictable and makes ROS 2 problems easier to diagnose.

---

## 15. Server Instructions vs. Safety Guardrails

This distinction is important.

### Server Instructions

Server Instructions provide guidance to the MCP client or LLM:

```text
What should I do?
How should I use the tools?
What workflow should I prefer?
What should I avoid requesting?
```

### Safety Guardrails

Server-side safety controls determine:

```text
What am I actually allowed to do?
```

The relationship is:

```text
LLM / MCP Client
       │
       │ Server Instructions
       ▼
Expected safe behavior
       │
       ▼
MCP Tools
       │
       ▼
Safety Guardrails
       │
       │ actual enforcement
       ▼
ROS 2 Runtime
```

Server Instructions are therefore **not treated as a security boundary**.

They complement the existing server-side safety architecture.

---

## 16. Phase 10 Diagnosis

Before implementation, Phase 10 tested the actual behavior of the installed MCP SDK.

The project uses:

```text
mcp 2.0.0
mcp-types 2.0.0
```

The diagnosis confirmed that:

```text
MCPServer supports instructions
```

and that the previous `ros2_mcp` server configuration had:

```text
server.instructions = None
```

This established that Server Instructions were not yet configured and could be added without changing the ROS 2 runtime architecture.

---

## 17. In-Process Client Observation

During diagnosis, a direct in-process MCP client was tested with a temporary server containing instructions.

The server contained the expected instructions.

However, with the tested direct client mode:

```text
client.instructions = None
```

This behavior was treated as an SDK/client-mode observation rather than a failure of MCP Server Instructions.

For that reason, the permanent transport verification uses the real STDIO MCP initialization path.

---

## 18. STDIO Verification

A real STDIO MCP initialization path was tested.

The initialization result contained the configured server instructions.

This confirms the required path:

```text
MCP Server
    │
    │ STDIO
    ▼
MCP ClientSession
    │
    │ initialize()
    ▼
InitializeResult.instructions
```

The Server Instructions were successfully delivered through the MCP initialization protocol.

---

## 19. Permanent Phase 10 Tests

The permanent integration tests are located at:

```text
tests/integration/test_server_instructions.py
```

Phase 10 adds two tests.

### Test 1

```text
test_server_exposes_instructions
```

This verifies that:

```text
create_server()
```

configures the expected Server Instructions.

It also verifies representative guidance including:

```text
controlled MCP interface
read-only inspection
dry-run
safety guardrails
```

### Test 2

```text
test_stdio_delivers_server_instructions
```

This starts the actual `ros2_mcp` module using STDIO:

```text
python -m ros2_mcp.server
```

It initializes a real MCP `ClientSession` and verifies:

```text
InitializeResult.instructions == SERVER_INSTRUCTIONS
```

The same test also verifies:

```text
Tool count == 46
```

This ensures that adding Server Instructions does not change the existing MCP tool inventory.

---

## 20. Why STDIO Is Tested

The local `ros2_mcp` deployment uses STDIO for MCP communication.

The permanent Phase 10 integration test therefore validates the transport path relevant for local MCP clients.

The test covers:

```text
Python process
      │
      ▼
ros2_mcp server
      │
      │ STDIO
      ▼
MCP ClientSession
      │
      ▼
initialize()
      │
      ├── Server Instructions
      │
      └── MCP capabilities
```

This provides stronger verification than only inspecting the Python `MCPServer` object.

---

## 21. Existing MCP Tool Inventory

Before Phase 10:

```text
46 MCP tools
```

After Phase 10:

```text
46 MCP tools
```

Verified result:

```text
Tool count: 46
```

Phase 10 therefore:

```text
adds no new ROS 2 tool
removes no existing ROS 2 tool
changes no intentional ROS 2 tool behavior
```

---

## 22. MCP 2026-07-28 Regression Protection

The permanent Phase 9 tests are re-run as part of Phase 10 verification.

Result:

```text
2 passed
```

This verifies that Server Instructions do not break the established:

```text
MCP 2026-07-28
```

protocol baseline.

The development sequence is therefore:

```text
Phase 9
Protocol baseline
      │
      ▼
Phase 10
Server Instructions
```

without replacing or weakening the Phase 9 guarantees.

---

## 23. Full Regression Result

Before Phase 10:

```text
22 tests
```

Phase 10 adds:

```text
2 tests
```

Current complete regression suite:

```text
24 passed
```

Test collection:

```text
24 tests collected
```

This confirms that the existing ROS 2 functionality continues to pass after Server Instructions were added.

---

## 24. Quality Checks

Phase 10 verifies:

```text
Server Instructions configuration: PASS
STDIO Instructions delivery: PASS
Phase 10 integration tests: PASS
Phase 9 protocol regression: PASS
Python syntax: PASS
Full pytest suite: PASS
Test collection: PASS
MCP protocol 2026-07-28: PASS
46-tool inventory: PASS
git diff --check: PASS
```

---

## 25. Files Added

Phase 10 adds:

```text
src/ros2_mcp/mcp/instructions.py
tests/integration/test_server_instructions.py
docs/README_PHASE_10.md
```

---

## 26. Files Modified

Phase 10 modifies:

```text
src/ros2_mcp/server.py
```

The modification connects:

```text
SERVER_INSTRUCTIONS
```

to:

```text
MCPServer
```

No ROS 2 adapter implementation is intentionally changed.

No runtime service implementation is intentionally changed.

No existing MCP tool implementation is intentionally changed.

---

## 27. What Phase 10 Does Not Implement

Phase 10 intentionally does not implement:

```text
MCP Prompts
MCP Resources
Client Compatibility Tests
Remote MCP / HTTP
Windows remote client support
macOS remote client support
```

These remain separate development phases.

This keeps each MCP capability isolated and independently testable.

---

## 28. Codex Compatibility

Phase 10 verifies the MCP STDIO transport used by local MCP clients.

A dedicated end-to-end Codex compatibility test is **not** part of Phase 10.

Client-specific testing is planned for the later Client Compatibility phase, where the same `ros2_mcp` server can be tested against multiple MCP clients.

The responsibilities remain separated:

```text
Phase 10
    │
    └── Server Instructions
        + STDIO protocol verification

Phase 13
    │
    └── Client Compatibility Tests
        ├── Codex
        ├── Claude Code
        └── other compatible MCP clients
```

This avoids mixing a server capability test with client-specific compatibility testing.

---

## 29. Planned Development Sequence

After Phase 10:

```text
Phase 9
MCP 2026-07-28 Compliance
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
        │
        ▼
Phase 14
Remote MCP / HTTP
```

The existing ROS 2 runtime remains the foundation underneath these MCP capabilities.

---

## 30. Current Architecture Status

After Phase 10:

```text
MCP Client / LLM
    │
    ├── MCP 2026-07-28
    ├── Server Instructions
    │
    ▼
ros2_mcp MCP Server
    │
    ├── 46 MCP Tools
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

The architectural separation remains:

```text
MCP
 │
 ▼
Application
 │
 ▼
ROS Adapter
 │
 ▼
ROS 2 Jazzy
```

Phase 10 only extends the MCP layer.

---

## 31. Phase 10 Final Status

Current verified status:

```text
Branch: dev

MCP SDK: 2.0.0
MCP Types: 2.0.0
MCP protocol baseline: 2026-07-28

Server Instructions: enabled
STDIO Instructions delivery: PASS

MCP tools: 46

Dedicated Phase 10 tests: 2 passed
Phase 9 regression tests: 2 passed
Complete regression suite: 24 passed
Test collection: 24 tests

Server Instructions configuration: PASS
STDIO initialization: PASS
Protocol verification: PASS
Tool inventory: PASS
Python syntax: PASS
Regression suite: PASS
Diff quality: PASS
```

---

## 32. Phase 10 Result

```text
PHASE 10 MCP SERVER INSTRUCTIONS: PASS
```

`ros2_mcp` now provides MCP Server Instructions while preserving:

```text
MCP 2026-07-28 protocol baseline
46 MCP ROS 2 tools
existing ROS 2 runtime architecture
existing server-side safety architecture
existing regression compatibility
```

Phase 10 establishes the guidance layer required before adding higher-level MCP capabilities such as Prompts and Resources.
