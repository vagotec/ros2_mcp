# Phase 12 – Modular MCP Resources

## 1. Goal

Phase 12 adds native MCP Resources to `ros2_mcp`.

The purpose of MCP Resources is to expose read-only ROS 2 runtime context to MCP clients without duplicating the existing runtime implementation.

Phase 12 builds on the previous MCP extension phases:

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
```

The existing ROS 2 runtime architecture remains authoritative.

No second ROS adapter is introduced.

---

## 2. Development Branch

Phase 12 is developed on:

```text
dev
```

The stable Version 1 implementation remains on:

```text
main
```

The Version 2 MCP extensions are developed and tested on `dev` before the final merge into `main`.

---

## 3. MCP Protocol Baseline

The required MCP protocol baseline remains:

```text
2026-07-28
```

The installed MCP packages used during Phase 12 development are:

```text
mcp:       2.0.0
mcp-types: 2.0.0
```

Phase 12 does not change the protocol baseline established by Phase 9.

---

## 4. MCP Capability Model

After Phase 12, the MCP-facing architecture contains four complementary capabilities:

```text
Server Instructions
MCP Tools
MCP Prompts
MCP Resources
```

Their responsibilities are intentionally different.

```text
Server Instructions
    │
    └── General guidance for safe and correct server usage

MCP Tools
    │
    └── Explicit ROS 2 operations and runtime queries

MCP Prompts
    │
    └── Reusable higher-level ROS 2 workflows

MCP Resources
    │
    └── Read-only ROS 2 runtime context
```

Resources do not replace tools.

Resources provide context that a client can read directly.

---

## 5. Architectural Principle

Phase 12 follows the same modular architecture principle already used by:

```text
ROS Adapter
MCP Prompts
```

The Resource architecture uses one central registration module and specialized resource modules.

```text
resources.py
    │
    └── resource/
        ├── runtime_health.py
        ├── safety_guardrails.py
        ├── nodes.py
        ├── topics.py
        ├── services.py
        ├── actions.py
        ├── node_info.py
        ├── topic_info.py
        └── action_info.py
```

The central module handles registration.

The specialized modules contain the individual resource definitions.

---

## 6. Phase 12 Project Structure

The MCP area now contains:

```text
src/ros2_mcp/mcp/
│
├── __init__.py
├── instructions.py
├── runtime_tools.py
├── prompts.py
├── resources.py
│
├── prompt/
│   ├── __init__.py
│   ├── ros_health_check.py
│   ├── diagnose_node.py
│   ├── diagnose_topic.py
│   ├── diagnose_action.py
│   ├── inspect_runtime_logs.py
│   └── safe_runtime_review.py
│
└── resource/
    ├── __init__.py
    ├── runtime_health.py
    ├── safety_guardrails.py
    ├── nodes.py
    ├── topics.py
    ├── services.py
    ├── actions.py
    ├── node_info.py
    ├── topic_info.py
    └── action_info.py
```

Responsibilities:

```text
instructions.py
    → Server Instructions

runtime_tools.py
    → 46 ROS 2 MCP Tools

prompts.py
    → MCP Prompt registration

prompt/
    → Individual MCP Prompt workflows

resources.py
    → MCP Resource registration

resource/
    → Individual MCP Resource implementations
```

---

## 7. Central Resource Registration

The central Resource registration module is:

```text
src/ros2_mcp/mcp/resources.py
```

Its responsibility is to register all Phase 12 resources with the MCP server.

Conceptually:

```text
server.py
    │
    ▼
register_resources(server)
    │
    ▼
resources.py
    │
    ├── runtime_health
    ├── safety_guardrails
    ├── nodes
    ├── topics
    ├── services
    ├── actions
    ├── node_info
    ├── topic_info
    └── action_info
```

This keeps `server.py` small.

---

## 8. Server Integration

The MCP server now configures:

```text
MCPServer
    │
    ├── Server Instructions
    ├── Runtime Tools
    ├── Prompts
    └── Resources
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
register_resources(server)
```

No ROS-specific implementation is moved into `server.py`.

---

## 9. Resource Runtime Architecture

Resources reuse the existing application architecture.

```text
MCP Client
    │
    │ resources/read
    ▼
MCP Resource
    │
    ▼
MCP Context
    │
    ▼
AppContext
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

The resource modules do not access `rclpy` directly.

They do not create a second ROS node.

They do not bypass the existing `RuntimeService`.

---

## 10. Context Injection

The MCP SDK injects a request `Context` into Resource Template handlers.

The Phase 12 implementation uses:

```python
app = ctx.request_context.lifespan_context
```

This is the same application-context access pattern already used by the existing MCP Tools.

The lifespan context contains:

```text
ros_adapter
runtime_service
settings
```

The Resource layer therefore has access to the existing `RuntimeService` without introducing global runtime state.

---

## 11. Why Resources Are Resource Templates

The current implementation exposes:

```text
0 static resources
9 resource templates
```

This is intentional.

The six runtime snapshot resources also need access to the MCP request context.

Therefore they use a `{scope}` template and currently support:

```text
scope = current
```

Examples:

```text
ros2://runtime/health/current
ros2://graph/nodes/current
```

This allows the MCP SDK to inject the request context required to reach `AppContext`.

---

## 12. Phase 12 Resource Inventory

Phase 12 introduces:

```text
9 MCP Resource Templates
```

They are:

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

The first six provide current runtime snapshots.

The last three provide information for specific ROS 2 entities.

---

## 13. Runtime Health Resource

Module:

```text
src/ros2_mcp/mcp/resource/runtime_health.py
```

Template:

```text
ros2://runtime/health/{scope}
```

Supported scope:

```text
current
```

Example:

```text
ros2://runtime/health/current
```

The resource calls:

```text
RuntimeService.get_runtime_health()
```

The timeout is taken from the existing runtime settings:

```text
settings.runtime.read_topic_timeout_sec
```

This preserves the behavior of the existing `get_runtime_health` MCP Tool.

---

## 14. Safety Guardrails Resource

Module:

```text
src/ros2_mcp/mcp/resource/safety_guardrails.py
```

Template:

```text
ros2://runtime/safety/{scope}
```

Supported scope:

```text
current
```

Example:

```text
ros2://runtime/safety/current
```

The resource exposes the active `ros2_mcp` runtime safety controls.

Representative guardrails include:

```text
arbitrary_shell = false
managed_process_stop_only = true
managed_launch_stop_only = true
managed_rosbag_stop_only = true
package_resolution_required = true
launch_file_resolution_required = true
structured_argument_validation = true
```

The resource is read-only.

---

## 15. Node Inventory Resource

Module:

```text
src/ros2_mcp/mcp/resource/nodes.py
```

Template:

```text
ros2://graph/nodes/{scope}
```

Example:

```text
ros2://graph/nodes/current
```

The resource returns the currently visible ROS 2 node inventory through:

```text
RuntimeService.list_nodes()
```

---

## 16. Topic Inventory Resource

Module:

```text
src/ros2_mcp/mcp/resource/topics.py
```

Template:

```text
ros2://graph/topics/{scope}
```

Example:

```text
ros2://graph/topics/current
```

The resource returns:

```text
topic name
message types
```

through:

```text
RuntimeService.list_topics()
```

---

## 17. Service Inventory Resource

Module:

```text
src/ros2_mcp/mcp/resource/services.py
```

Template:

```text
ros2://graph/services/{scope}
```

Example:

```text
ros2://graph/services/current
```

The resource returns:

```text
service name
service types
```

through:

```text
RuntimeService.list_services()
```

---

## 18. Action Inventory Resource

Module:

```text
src/ros2_mcp/mcp/resource/actions.py
```

Template:

```text
ros2://graph/actions/{scope}
```

Example:

```text
ros2://graph/actions/current
```

The resource returns:

```text
action name
action types
```

through:

```text
RuntimeService.list_actions()
```

---

## 19. Node Information Resource

Module:

```text
src/ros2_mcp/mcp/resource/node_info.py
```

Template:

```text
ros2://node/{node_name}
```

Example logical ROS name:

```text
/robot1/camera
```

The resource returns the same node runtime information used by the existing:

```text
node_info
```

MCP Tool.

The implementation calls:

```text
RuntimeService.node_info(node_name)
```

---

## 20. Topic Information Resource

Module:

```text
src/ros2_mcp/mcp/resource/topic_info.py
```

Template:

```text
ros2://topic/{topic_name}
```

Example logical ROS name:

```text
/robot1/camera/image_raw
```

The resource calls:

```text
RuntimeService.topic_info(topic_name)
```

It provides read-only context about one ROS 2 topic.

---

## 21. Action Information Resource

Module:

```text
src/ros2_mcp/mcp/resource/action_info.py
```

Template:

```text
ros2://action/{action_name}
```

Example logical ROS name:

```text
/robot1/navigate_to_pose
```

The resource calls:

```text
RuntimeService.action_info(action_name)
```

It does not send or cancel action goals.

---

## 22. ROS Name Handling

ROS 2 entity names frequently begin with:

```text
/
```

and may contain nested namespaces:

```text
/robot1/camera/image_raw
```

The MCP SDK applies generic Resource security validation to template parameters.

Because ROS names are not filesystem paths, Phase 12 applies targeted exemptions only to the ROS-name parameters:

```text
node_name
topic_name
action_name
```

The implementation does not disable Resource security globally.

It validates that these entity names:

```text
start with /
do not contain null bytes
```

This allows absolute ROS names while preserving the normal MCP security behavior for other Resource parameters.

---

## 23. Resource Security Design

Phase 12 deliberately avoids a broad security configuration such as disabling all absolute-path validation.

Instead, only the semantically special ROS name parameters are exempted.

Conceptually:

```text
ResourceSecurity
    │
    ├── normal validation remains active
    │
    └── targeted exemption
            │
            ├── node_name
            ├── topic_name
            └── action_name
```

This keeps the Resource layer narrowly permissive only where ROS naming requires it.

---

## 24. Read-Only Design

The complete Phase 12 Resource layer is read-only.

Resources do not:

```text
publish messages
call state-changing services
send action goals
cancel action goals
start processes
stop processes
start launches
stop launches
record rosbag
play rosbag
modify parameters
```

Those operations remain MCP Tool responsibilities.

---

## 25. Tools vs Prompts vs Resources

The architecture after Phase 12 is intentionally explicit.

```text
MCP Tool
    → perform an explicit operation or runtime query

MCP Prompt
    → describe a reusable workflow

MCP Resource
    → provide read-only runtime context
```

Example:

```text
User wants topic diagnosis
        │
        ▼
diagnose_topic Prompt
        │
        ▼
LLM decides what information is needed
        │
        ├── topic_info Tool
        ├── QoS Tool
        └── ros2://topic/... Resource
```

Each MCP capability has a distinct responsibility.

---

## 26. Resource Integration Tests

The permanent Phase 12 tests are located at:

```text
tests/integration/test_mcp_resources.py
```

Phase 12 adds four tests:

```text
test_resource_inventory
test_snapshot_resources
test_entity_resources_preserve_ros_names
test_invalid_resource_scope_is_rejected
```

---

## 27. Resource Inventory Test

The inventory test verifies that the existing MCP capabilities remain available.

Expected state:

```text
MCP protocol:      2026-07-28
Tools:             46
Prompts:            6
Static Resources:   0
Resource Templates: 9
```

The exact expected Resource Templates are verified.

---

## 28. Snapshot Resource Test

The snapshot test verifies:

```text
ros2://runtime/health/current
ros2://runtime/safety/current
ros2://graph/nodes/current
ros2://graph/topics/current
ros2://graph/services/current
ros2://graph/actions/current
```

The test uses a deterministic fake `RuntimeService` through the MCP lifespan context.

This verifies the complete path:

```text
MCP resources/read
        │
        ▼
Resource handler
        │
        ▼
Context
        │
        ▼
RuntimeService
```

without requiring a live external ROS system.

---

## 29. Entity Resource Test

The entity Resource test verifies that namespaced ROS 2 names survive the Resource Template path.

Representative values include:

```text
/robot1/camera
/robot1/camera/image_raw
/robot1/navigate_to_pose
```

The resulting Resource content must contain the original ROS name.

This permanently protects ROS namespace handling.

---

## 30. Invalid Scope Test

The current snapshot Resources support only:

```text
current
```

An unsupported scope such as:

```text
future
```

must be rejected.

This prevents clients from assuming that the server provides historical or predictive snapshots that do not exist.

---

## 31. Phase 9 Regression

The Phase 9 MCP protocol tests remain green after the Phase 12 implementation.

Result:

```text
2 passed
```

The required protocol baseline remains:

```text
2026-07-28
```

---

## 32. Phase 10 Regression

The Phase 10 Server Instructions tests remain green.

Result:

```text
2 passed
```

Resources therefore coexist with Server Instructions.

---

## 33. Phase 11 Regression

The Phase 11 MCP Prompt tests remain green.

Result:

```text
3 passed
```

Resources therefore coexist with the six existing MCP Prompts.

---

## 34. Full Regression Suite

Before Phase 12:

```text
27 tests
```

Phase 12 adds:

```text
4 tests
```

The complete regression result is:

```text
31 passed
```

Test collection result:

```text
31 tests collected
```

Additional checks:

```text
Python syntax: PASS
git diff --check: PASS
```

---

## 35. Real Codex Client Test

Phase 12 was also tested with a real external MCP client:

```text
OpenAI Codex CLI
v0.147.0
```

Codex was connected to the development server registered as:

```text
ros2_mcp_dev
```

The registration uses the current `dev` checkout:

```text
~/projects/robotics/ros2_mcp
```

and starts the installed project executable:

```text
ros2-mcp
```

with ROS 2 Jazzy sourced.

---

## 36. Clean Codex MCP Environment

Before the final Codex compatibility test, broken and unrelated MCP registrations were removed.

Removed registrations included:

```text
github
ros2_mcp
MCP_DOCKER
docker
```

The outdated `ros2_mcp` entry still referenced a previously removed test installation and was therefore intentionally deleted.

The final relevant ROS MCP registrations were:

```text
ros2_dev_mcp
ros2_mcp_dev
```

Codex then started without the previous MCP startup warnings.

---

## 37. Codex Resource Discovery Test

Codex successfully discovered:

```text
0 static resources
9 resource templates
```

The nine templates were:

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

The discovery result matched the Phase 12 expected inventory exactly.

---

## 38. Codex Runtime Resource Read Test

Codex successfully performed real MCP `resources/read` operations against:

```text
ros2://runtime/health/current
ros2://runtime/safety/current
```

The runtime health resource returned:

```text
health: OK
```

together with ROS graph, diagnostics, and runtime information.

The safety resource returned the active `ros2_mcp` guardrails.

Both operations completed successfully through the real Codex MCP client.

---

## 39. Extended Codex Resource Test

An earlier full Phase 12 Codex test also successfully read:

```text
ros2://graph/nodes/current
ros2://graph/topics/current
ros2://graph/services/current
ros2://graph/actions/current
```

All requested Resource reads completed successfully.

The result was:

```text
ros2_mcp_dev connection:     PASS
Resource template discovery: PASS
Runtime health resource:     PASS
Safety resource:             PASS
Node inventory resource:     PASS
Topic inventory resource:    PASS
Service inventory resource:  PASS
Action inventory resource:   PASS
```

No files or ROS runtime state were intentionally modified.

---

## 40. Live ROS 2 Result During Codex Test

During the real Codex resource test, the current runtime health reported:

```text
health: OK
```

The visible topic inventory included:

```text
/parameter_events
/rosout
```

The public node, service, and action inventory Resources were empty at that moment.

The runtime health summary internally reported additional graph entities.

This is compatible with the existing filtering behavior used by `ros2_mcp`, where internal or introspection entities may be filtered from public inventory results.

Phase 12 did not change that filtering behavior.

---

## 41. Codex Compatibility Boundary

The Codex Resource test directly verified:

```text
MCP server connection
Resource template discovery
Resource reading
runtime health
runtime safety
graph Resources
```

The Resource-only Codex calls do not independently expose all server metadata.

Therefore values such as:

```text
46 Tools
6 Prompts
MCP protocol 2026-07-28
```

remain primarily verified by the permanent MCP integration tests.

The real Codex client independently verified the Resource capability.

---

## 42. Current MCP Inventory

After Phase 12:

```text
MCP protocol baseline: 2026-07-28

Server Instructions: 1 configuration

MCP Tools:             46
MCP Prompts:            6
Static Resources:       0
Resource Templates:     9
```

This gives the server three distinct user-facing MCP capability groups:

```text
46 Tools
6 Prompts
9 Resource Templates
```

---

## 43. Phase 12 Quality Results

The implementation verification produced:

```text
Resource inventory:    PASS
Phase 12 tests:        PASS
Phase 11 regression:   PASS
Phase 10 regression:   PASS
Phase 9 regression:    PASS
Python syntax:         PASS
Full pytest:           PASS
Test collection:       PASS
Diff quality:          PASS
```

Dedicated Phase 12 tests:

```text
4 passed
```

Complete project test suite:

```text
31 passed
```

---

## 44. Codex Compatibility Results

Real Codex client:

```text
Codex CLI: v0.147.0

ros2_mcp_dev connection:      PASS
Clean MCP startup:            PASS
Resource discovery:           PASS
9 Resource Templates:         PASS
Runtime Health read:          PASS
Runtime Safety read:          PASS
Node Inventory read:          PASS
Topic Inventory read:         PASS
Service Inventory read:       PASS
Action Inventory read:        PASS
```

No project files were intentionally modified during these client tests.

---

## 45. What Phase 12 Does Not Implement

Phase 12 intentionally does not implement:

```text
Remote MCP / HTTP
Windows remote MCP client access
macOS remote MCP client access
multi-client compatibility matrix
resource subscriptions
resource update notifications
historical runtime snapshots
persistent resource cache
```

These belong to later development phases.

---

## 46. Current Version 2 Development Sequence

The Version 2 MCP extension sequence now stands at:

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
        │ IMPLEMENTED / TESTED
        ▼
Phase 13
Client Compatibility Tests
        │
        ▼
Phase 14
Remote MCP / HTTP
```

---

## 47. Future Resource Extensions

The modular architecture allows new Resources to be added without growing `resources.py` into a monolithic file.

Possible future Resource families include:

```text
resource/
│
├── runtime/
├── graph/
├── diagnostics/
├── ros2_control/
├── moveit/
└── nav2/
```

The central registration module can remain the composition layer.

---

## 48. Separation From Specialized MCP Servers

The Codex environment currently also contains:

```text
ros2_dev_mcp
```

This is a separate MCP server focused on ROS 2 project development operations such as:

```text
create_workspace
create_package
create_node
create_launch_file
create_parameter_file
create_tests
build_project
run_tests
```

It is independent from the current runtime server:

```text
ros2_mcp_dev
```

The runtime server remains responsible for observing, diagnosing, and controlling an active ROS 2 runtime.

---

## 49. Development Registration Naming

The project itself is:

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

During development, the Codex MCP registration is intentionally named:

```text
ros2_mcp_dev
```

This distinguishes the current `dev` implementation from the stable server.

After Version 2 is complete and merged into `main`, the development registration can be removed and the final server can again be registered as:

```text
ros2_mcp
```

---

## 50. Phase 12 Final Status

Current verified development state:

```text
Branch: dev

MCP protocol baseline:
2026-07-28

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

Resource discovery:
PASS

Resource context injection:
PASS

RuntimeService integration:
PASS

ROS absolute-name handling:
PASS

Snapshot resource reads:
PASS

Entity resource reads:
PASS

Resource security:
PASS

Phase 9 regression:
PASS

Phase 10 regression:
PASS

Phase 11 regression:
PASS

Phase 12 tests:
4 passed

Complete test suite:
31 passed

Codex v0.147.0:
PASS

Codex clean MCP startup:
PASS

Codex Resource discovery:
PASS

Codex Resource reads:
PASS

Python syntax:
PASS

Diff quality:
PASS
```

## Phase 12 Result

```text
PHASE 12 MODULAR MCP RESOURCES: PASS
```

Phase 12 adds a modular, read-only MCP Resource layer to `ros2_mcp` while preserving the existing application runtime architecture, ROS adapter abstraction, 46 MCP Tools, 6 MCP Prompts, Server Instructions, safety controls, and MCP `2026-07-28` protocol baseline.
