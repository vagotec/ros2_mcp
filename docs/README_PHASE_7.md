# Phase 7 – Advanced ROS 2 Runtime Operations

Phase 7 extends `ros2_mcp` from basic ROS 2 runtime access into a more complete, modular, and safety-controlled ROS 2 runtime integration layer.

The implementation targets:

- ROS 2 Jazzy
- Python 3.12
- `rclpy`
- MCP Python SDK
- Codex as an MCP client

The goal of this phase is to expose important ROS 2 runtime functionality through MCP without exposing arbitrary shell execution.

The final Phase 7 implementation provides:

- ROS graph discovery
- topic inspection
- topic reading
- multi-message topic reading
- topic publishing
- automatic QoS discovery and recommendation
- persistent publishers
- service discovery and calls
- parameter access
- action discovery
- action inspection
- action execution
- long-running action lifecycle management
- ROS interface discovery
- `/rosout` inspection
- ROS diagnostics
- runtime health aggregation
- ROS process management
- ROS launch management
- ROS lifecycle node operations
- rosbag2 recording and playback management
- safety guardrails
- executor serialization
- modular ROS 2 Jazzy adapter architecture

Image and camera retrieval are intentionally not part of `ros2_mcp`.

Camera-specific functionality is planned for a separate MCP component.

---

# 1. Architecture

Phase 7 preserves the architectural separation between MCP, application logic, and ROS 2.

The runtime path remains:

```text
Codex / MCP Client
        │
        ▼
MCP Runtime Tools
        │
        ▼
RuntimeService
        │
        ▼
RosAdapter
        │
        ▼
JazzyRosAdapter
        │
        ▼
ROS 2 Jazzy / rclpy
```

The important rule is:

```text
MCP does not directly depend on rclpy.
```

ROS-specific behavior remains behind the `RosAdapter` abstraction.

This allows later ROS distributions or alternative ROS adapters to be introduced without changing the MCP interface.

---

# 2. Four-Layer Runtime Design

ROS runtime functionality is implemented through four layers.

## Layer 1 – ROS Adapter Contract

```text
src/ros2_mcp/ros/adapter.py
```

Defines the abstract ROS runtime API.

The application layer does not depend directly on `rclpy`.

---

## Layer 2 – Application Runtime Service

```text
src/ros2_mcp/application/runtime/service.py
```

Provides the application-facing runtime operations.

The service delegates ROS-specific behavior to `RosAdapter`.

---

## Layer 3 – ROS 2 Jazzy Implementation

```text
src/ros2_mcp/ros/jazzy/
```

Contains the ROS 2 Jazzy implementation based on:

```text
rclpy
rosidl_runtime_py
ament_index_python
ros2action
rosbag2
ROS lifecycle services
```

where required by the individual runtime feature.

---

## Layer 4 – MCP Runtime Tools

```text
src/ros2_mcp/mcp/runtime_tools.py
```

Exposes the runtime operations to MCP clients such as Codex.

The resulting flow is:

```text
Codex
   │
   ▼
MCP Tool
   │
   ▼
RuntimeService
   │
   ▼
RosAdapter
   │
   ▼
JazzyRosAdapter
   │
   ▼
ROS 2
```

---

# 3. Modular ROS 2 Jazzy Architecture

During Phase 7 the original large Jazzy adapter was modularized.

The main adapter is now primarily responsible for:

- ROS context creation
- ROS node creation
- executor creation
- shared executor synchronization
- resource registries
- mixin composition
- cleanup

The ROS functionality is separated into dedicated modules.

Final structure:

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

The main adapter was reduced from more than 2,000 lines to approximately 150 lines after modularization.

Its primary methods are now essentially:

```text
__init__
close
```

plus shared runtime infrastructure.

---

# 4. Jazzy Adapter Composition

`JazzyRosAdapter` composes the individual ROS capabilities through mixins.

The final MRO includes:

```text
JazzyRosAdapter
GraphMixin
TopicsMixin
ServicesMixin
ParametersMixin
ActionsMixin
LoggingMixin
DiagnosticsMixin
InterfacesMixin
QoSMixin
PublishersMixin
ProcessMixin
LaunchMixin
LifecycleMixin
RosbagMixin
AutoQoSMixin
SafetyMixin
RosAdapter
ABC
object
```

This prevents the ROS 2 Jazzy implementation from becoming a single monolithic file.

---

# 5. ROS Graph Discovery

Phase 7 supports ROS graph inspection.

Important operations include:

```text
list_nodes
list_topics
topic_info
list_services
service_info
node_info
```

These operations allow an MCP client to discover the currently running ROS system without using shell commands.

Example conceptual request:

```text
List all ROS 2 nodes.
```

The request flows through:

```text
Codex
→ ros2_mcp.list_nodes
→ RuntimeService
→ JazzyRosAdapter
→ rclpy ROS graph
```

---

# 6. Topic Reading

`ros2_mcp` can read ROS topic messages dynamically.

The message type is discovered from the ROS graph.

The corresponding ROS message class is resolved dynamically.

Example supported type:

```text
std_msgs/msg/String
```

The returned message is converted into a normal Python/MCP-compatible structure.

Example:

```json
{
  "topic": "/example",
  "type": "std_msgs/msg/String",
  "message": {
    "data": "hello"
  }
}
```

---

# 7. Multi-Message Topic Reading

Phase 7 adds:

```text
read_topic_messages
```

This allows multiple messages to be collected from a topic during one MCP call.

Important parameters include:

```text
topic_name
max_messages
duration_sec
qos
```

Example conceptual request:

```text
Read exactly 5 messages from /example for a maximum of 2 seconds.
```

The result contains:

```text
topic
type
count
max_messages
duration_sec
messages
qos
```

This is important for:

- telemetry
- sensor streams
- state monitoring
- debugging
- short observation windows

It also becomes useful later for:

- LiDAR metadata
- joint states
- odometry
- navigation status
- robot state streams

Actual image retrieval remains outside this MCP server.

---

# 8. Topic Publishing

Phase 7 supports controlled topic publishing.

The operation:

```text
publish_topic
```

dynamically resolves the ROS message type and converts MCP/Python data into a ROS message.

Example:

```text
Topic:
/example

Type:
std_msgs/msg/String

Message:
{"data": "hello"}
```

Safety validation is performed before writes to protected topics.

---

# 9. Persistent Publishers

Normal one-shot publishing creates a temporary publisher.

Some ROS applications require a publisher to remain alive across multiple MCP calls.

Phase 7 therefore adds a persistent publisher registry.

The lifecycle is:

```text
create_persistent_publisher
        │
        ▼
publisher_id
        │
        ├── publish_with_publisher
        ├── publish_with_publisher
        ├── publish_with_publisher
        │
        ▼
destroy_persistent_publisher
```

Available tools:

```text
create_persistent_publisher
publish_with_publisher
list_persistent_publishers
destroy_persistent_publisher
```

Each persistent publisher stores information such as:

```text
publisher_id
topic
type
QoS
publish_count
subscriber_count
```

A real ROS subscriber test successfully received multiple messages from the same persistent publisher.

---

# 10. QoS Support

ROS 2 communication depends heavily on DDS QoS compatibility.

Phase 7 supports configurable QoS for topic reading and publishing.

Supported policies include:

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

Invalid QoS values are rejected.

Examples of validation errors include:

```text
QoS reliability must be reliable or best_effort.

QoS durability must be volatile or transient_local.

QoS history must be keep_last or keep_all.

QoS depth must be a positive integer.
```

---

# 11. QoS Discovery

Phase 7 adds runtime QoS discovery.

Tool:

```text
get_topic_qos
```

It inspects publishers and subscriptions associated with a topic.

Example discovered publisher QoS:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

This information can be used before creating a subscription.

---

# 12. Automatic QoS Recommendation

Phase 7 adds:

```text
recommend_topic_qos
```

The tool derives a compatible QoS profile from the discovered endpoints.

Example:

```text
Topic:
/mcp_final_codex_topic

Publisher:
BEST_EFFORT
VOLATILE
KEEP_LAST
depth 7
```

Recommended subscription:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

---

# 13. Automatic QoS Topic Reading

An important issue was found during the final Codex integration test.

Initially:

```text
read_topic()
```

without an explicit QoS configuration selected the default profile:

```text
reliable
volatile
keep_last
depth 10
```

The test publisher used:

```text
best_effort
volatile
keep_last
depth 7
```

ROS 2 correctly reported:

```text
incompatible QoS
Last incompatible policy: RELIABILITY
```

The automatic reader therefore received:

```text
message: null
```

Phase 7 was corrected so that default topic reading uses automatic QoS discovery.

After the fix, the selected profile was:

```text
history: keep_last
depth: 7
reliability: best_effort
durability: volatile
```

A real ROS test then successfully received:

```text
auto qos fixed 6
```

This means automatic topic reading now follows the discovered ROS publisher QoS instead of blindly using a fixed reliable profile.

---

# 14. Services

Phase 7 supports ROS service discovery and invocation.

Important tools include:

```text
list_services
service_info
call_service
```

Service types are dynamically resolved.

Requests are converted from MCP/Python structures into ROS service requests.

Responses are converted back into MCP-compatible structures.

---

# 15. Parameters

Phase 7 supports ROS parameter operations.

Available operations include:

```text
list_parameters
get_parameter
set_parameter
```

The parameter operations work through ROS services exposed by ROS nodes.

Write operations pass through the safety layer.

---

# 16. ROS Actions

Phase 7 provides both simple and managed ROS action operations.

The implementation supports:

```text
send_action_goal
start_action_goal
get_action_status
cancel_action_goal
```

---

# 17. Managed Action Goal Lifecycle

Long-running actions require state to survive multiple MCP calls.

Phase 7 therefore introduces an action goal registry.

The lifecycle is:

```text
start_action_goal
        │
        ▼
goal_id
        │
        ├── get_action_status
        │
        ├── get_action_status
        │
        ▼
cancel_action_goal
        │
        ▼
get_action_status
```

Stored state includes:

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

A real cancellable Fibonacci action was tested.

Observed states included:

```text
EXECUTING
CANCELING
CANCELED
```

The action server accepted the cancellation and returned the final result.

---

# 18. Action Discovery

Phase 7 adds explicit ROS action graph discovery.

Tool:

```text
list_actions
```

ROS 2 Jazzy provides action discovery APIs through `ros2action.api`, including:

```text
get_action_names
get_action_names_and_types
get_action_clients_and_servers
```

The implementation uses the ROS action discovery API rather than parsing shell output.

Example result:

```text
/mcp_final/fibonacci
example_interfaces/action/Fibonacci
```

---

# 19. Action Inspection

Phase 7 adds:

```text
action_info
```

It provides information about an action including:

```text
name
types
server_count
client_count
servers
clients
transport
```

Example:

```text
name:
/mcp_final/fibonacci

type:
example_interfaces/action/Fibonacci

server:
/mcp_final_codex_server
```

Action transport information includes the ROS action protocol endpoints such as:

```text
_action/send_goal
_action/get_result
_action/cancel_goal
```

---

# 20. ROS Interface Discovery

Phase 7 adds interface discovery.

Tools:

```text
list_interfaces
interface_info
```

Supported interface kinds include:

```text
msg
srv
action
```

Example message inspection:

```text
std_msgs/msg/String
```

Result:

```text
package: std_msgs
kind: msg
interface: String

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

# 21. ROS Logging

Phase 7 supports ROS log inspection through:

```text
read_rosout
```

The implementation reads:

```text
/rosout
```

and supports filtering by:

```text
node_name
minimum log level
maximum message count
```

Supported log levels include:

```text
DEBUG
INFO
WARN
ERROR
FATAL
```

A real ROS test generated recurring errors:

```text
codex rosout error 14
codex rosout error 15
codex rosout error 16
codex rosout error 17
codex rosout error 18
codex rosout error 19
```

Codex successfully retrieved them through `ros2_mcp`.

---

# 22. ROS Diagnostics

Phase 7 adds:

```text
get_diagnostics
```

It reads:

```text
/diagnostics
```

using:

```text
diagnostic_msgs/msg/DiagnosticArray
```

Diagnostic levels are:

```text
OK
WARN
ERROR
STALE
```

A compatibility issue was discovered during testing because the generated ROS Python representation of:

```text
DiagnosticStatus.level
```

could appear as a byte value.

The implementation was corrected to normalize ROS integer representations before comparing diagnostic levels.

Real diagnostic messages were then successfully processed.

---

# 23. Runtime Health

Phase 7 adds:

```text
get_runtime_health
```

The health summary combines:

```text
ROS graph
diagnostics
rosout
```

Example result:

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

The resulting health state can be:

```text
OK
WARN
ERROR
```

This provides an MCP client with a compact ROS runtime overview.

---

# 24. Executor Serialization

A concurrency issue was discovered during a real Codex MCP test.

Multiple MCP calls could attempt to spin the same ROS executor concurrently.

The resulting ROS error was:

```text
Executor is already spinning
```

Phase 7 therefore introduced shared executor serialization.

The main Jazzy adapter now owns an executor lock.

ROS modules use shared helper methods rather than directly spinning the executor independently.

The remaining direct executor calls are centralized in the adapter helper implementation.

A concurrent MCP test executed operations including:

```text
get_runtime_health
list_nodes
list_topics
get_runtime_health
```

without triggering the previous executor conflict.

Result:

```text
CONCURRENT EXECUTOR TEST: PASSED
```

---

# 25. ROS Process Management

Phase 7 adds controlled ROS process management.

Tools:

```text
start_ros_process
get_ros_process
list_ros_processes
stop_ros_process
```

Processes are started using structured arguments.

Arbitrary shell execution is not exposed.

The implementation resolves ROS package executables before starting them.

Example dry run:

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

Dry-run result:

```text
dry_run: true
```

No process is started during a dry run.

---

# 26. ROS Launch Management

Phase 7 adds managed ROS launch execution.

Tools:

```text
start_ros_launch
get_ros_launch
list_ros_launches
stop_ros_launch
```

Launch files must resolve through the ROS package/ament environment.

A temporary real ROS 2 package was registered through the ament resource index during integration testing.

The test launch file started a real ROS node:

```text
mcp_launch_test_talker
```

The complete lifecycle was verified:

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

# 27. ROS Lifecycle Nodes

Phase 7 adds ROS lifecycle node support.

Tools:

```text
get_lifecycle_state
change_lifecycle_state
```

These operations use ROS lifecycle interfaces instead of shell commands.

This allows MCP clients to inspect and control managed lifecycle nodes.

Typical lifecycle transitions include:

```text
configure
activate
deactivate
cleanup
shutdown
```

depending on the lifecycle node and its current state.

---

# 28. rosbag2 Recording

Phase 7 adds controlled rosbag recording.

Tools:

```text
start_bag_recording
stop_bag_recording
get_bag_info
```

Recording is managed by `ros2_mcp`.

Arbitrary paths are not accepted as unmanaged names.

Bag names are validated by the safety layer.

Dry-run mode is supported.

Example:

```text
bag:
final_dry_run

topics:
/chatter
```

Example resolved path:

```text
/home/sarvg/projects/robotics/ros2_mcp/bags/final_dry_run
```

---

# 29. rosbag2 Playback

Phase 7 also supports managed bag playback.

Tools:

```text
start_bag_playback
stop_bag_playback
```

Playback processes are registered and can only be stopped through their managed resource identifiers.

Dry-run mode is supported.

---

# 30. Safety Guardrails

Phase 7 introduces explicit runtime safety controls.

The safety module is:

```text
src/ros2_mcp/ros/jazzy/safety.py
```

The safety layer protects write and runtime operations.

Important properties include:

```text
arbitrary_shell: false

managed_process_stop_only: true
managed_launch_stop_only: true
managed_rosbag_stop_only: true

package_resolution_required: true
launch_file_resolution_required: true

path_traversal_for_managed_names: false

structured_argument_validation: true
```

---

# 31. Protected ROS Resources

The default protected topics include:

```text
/parameter_events
/rosout
```

Writing to these topics is blocked.

Example:

```text
publish_topic("/rosout", ...)
```

results in:

```text
PermissionError
```

The safety architecture also supports configured protection for:

```text
topics
services
parameters
actions
```

---

# 32. Runtime Resource Limits

Phase 7 introduces limits for managed resources.

The verified configuration includes limits such as:

```text
persistent_publishers: 32
managed_processes: 16
managed_launches: 8
bag_recordings: 4
bag_playbacks: 4
```

These limits prevent uncontrolled accumulation of runtime resources.

---

# 33. Package Allow Lists

The safety policy supports package allow lists for:

```text
ROS processes
ROS launches
```

The configuration can therefore restrict runtime execution to explicitly approved ROS packages when required.

An empty allow list currently means no additional package restriction is configured beyond the normal package resolution and structural safety checks.

---

# 34. Structured Argument Validation

Process arguments are passed as structured argument lists.

The MCP server does not expose arbitrary shell command execution.

Arguments are checked for unsafe content including:

```text
NUL
newline
carriage return
excessive argument length
excessive argument count
```

Managed package and executable names are also validated.

Path separators are rejected where simple ROS resource names are expected.

---

# 35. Dry-Run Support

The following managed runtime operations support dry-run mode:

```text
start_ros_process
start_ros_launch
start_bag_recording
start_bag_playback
```

Dry-run mode resolves and validates the requested operation without starting the actual resource.

This is useful for AI-controlled runtime planning because an MCP client can first validate an operation before executing it.

---

# 36. Configuration

Phase 7 extends:

```text
config/ros2_mcp.toml
```

Configuration is loaded through:

```text
src/ros2_mcp/config/settings.py
```

The configuration contains runtime and safety-related settings.

The configuration layer remains separate from ROS-specific implementation logic.

---

# 37. Image Retrieval Decision

Image retrieval is intentionally excluded from `ros2_mcp`.

The reason is architectural separation.

`ros2_mcp` is responsible for generic ROS runtime operations.

Camera-specific capabilities such as:

```text
image acquisition
compressed images
depth images
camera calibration
point clouds derived from cameras
camera stream inspection
camera-specific metadata
```

will be handled by a separate camera-focused MCP component.

Conceptually:

```text
ros2_mcp
    generic ROS 2 runtime

ros2_control_mcp
    robot hardware/control

ros2_nav_mcp
    Nav2

ros2_moveit_mcp
    MoveIt 2

mcp_camera
    cameras / image retrieval
```

This keeps the generic ROS MCP server focused and modular.

---

# 38. Final MCP Tool Inventory

At the end of Phase 7, `ros2_mcp` exposes 46 MCP tools.

The final inventory includes:

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

Total:

```text
46 tools
```

---

# 39. Final Core Tool Additions

The last three ROS 2 core additions completed during Phase 7 were:

```text
list_actions
action_info
read_topic_messages
```

They filled important gaps in:

```text
action discovery
action inspection
multi-message observation
```

---

# 40. Real Codex Integration Test

The final three core tools were tested from Codex using only `ros2_mcp`.

The test environment exposed:

```text
Action:
/mcp_final/fibonacci

Type:
example_interfaces/action/Fibonacci

Server:
/mcp_final_codex_server
```

and:

```text
Topic:
/mcp_final/multi_messages
```

The Codex request was:

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

Codex used:

```text
list_actions
action_info
read_topic_messages
```

The Fibonacci action was discovered successfully.

The action type was:

```text
example_interfaces/action/Fibonacci
```

The server was:

```text
/mcp_final_codex_server
```

Five messages were successfully received:

```text
codex multi message 326
codex multi message 327
codex multi message 328
codex multi message 329
codex multi message 330
```

Automatically selected QoS:

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

# 41. Earlier Final Codex Runtime Verification

A broader Codex verification tested:

```text
list_nodes
topic_info
get_topic_qos
recommend_topic_qos
read_topic
interface_info
list_interfaces
get_runtime_health
get_safety_guardrails
start_ros_process
```

The test exposed two important issues:

```text
automatic QoS mismatch
executor already spinning
```

Both issues were subsequently corrected during Phase 7.

After correction:

```text
default Auto-QoS test: PASSED

concurrent executor test: PASSED
```

This is an important part of Phase 7 because the final implementation was not accepted solely on unit tests; it was also exercised through a real MCP client and real ROS 2 endpoints.

---

# 42. Testing Strategy

Phase 7 uses several levels of verification.

```text
Python syntax checks
        │
        ▼
unit/regression tests
        │
        ▼
adapter contract checks
        │
        ▼
real ROS 2 integration tests
        │
        ▼
MCP client tests
        │
        ▼
Codex end-to-end tests
```

This is important because many ROS runtime issues cannot be detected through mocked unit tests alone.

Examples discovered only through real runtime testing included:

```text
DiagnosticStatus byte conversion
QoS incompatibility
executor concurrent spinning
action graph discovery behavior
launch package resolution
```

---

# 43. Final Unit and Regression Test Status

The final Phase 7 test suite contains:

```text
11 tests
```

Final result:

```text
...........                                                      [100%]

11 passed
```

The Python syntax check also completes successfully.

---

# 44. Environment Setup

Before running `ros2_mcp`, activate both the Python environment and ROS 2 Jazzy.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

When explicitly configuring the ROS domain and middleware:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

# 45. Run the MCP Server Directly

The MCP server can be started directly with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m ros2_mcp.server
```

The MCP server uses standard I/O transport when launched this way.

The terminal remains occupied by the MCP server until it is stopped.

---

# 46. Start Codex with ros2_mcp

Start Codex from the project directory so the project remains the active working directory.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
```

Inside Codex, inspect configured MCP servers with:

```text
/mcp
```

The ROS MCP server should appear as:

```text
ros2_mcp
```

---

# 47. Codex MCP Registration

If `ros2_mcp` needs to be registered again with Codex, an example registration is:

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

Inspect the registration with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2_mcp
```

---

# 48. Syntax Check

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
```

Expected result:

```text
exit code 0
```

Normally no output is produced when the syntax check succeeds.

---

# 49. Unit and Regression Tests

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q
```

Expected final Phase 7 result:

```text
11 passed
```

---

# 50. Complete Local Regression Check

Run syntax and tests together:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
```

Expected:

```text
syntax check successful
11 passed
```

---

# 51. ROS Graph Developer Test

For independent developer-side verification:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2 node list
ros2 topic list
ros2 service list
ros2 action list -t
```

These commands are developer-side checks.

They are not arbitrary shell capabilities exposed through the MCP server.

---

# 52. Adapter Architecture Check

Check the size and modular structure:

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

Expected architecture:

```text
small adapter.py

plus dedicated modules for:

actions
diagnostics
graph
interfaces
launches
lifecycle
logging
parameters
processes
publishers
qos
qos_auto
rosbag
safety
services
topics
```

---

# 53. Abstract Adapter Contract Test

The Jazzy adapter must implement every abstract method defined by `RosAdapter`.

Run:

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

# 54. Safety Guardrail Test

Inspect the current safety policy:

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

Important expected properties include:

```text
arbitrary_shell: false

managed_process_stop_only: true
managed_launch_stop_only: true
managed_rosbag_stop_only: true

package_resolution_required: true
launch_file_resolution_required: true

protected_topics:
    /parameter_events
    /rosout
```

---

# 55. Safety Negative Tests

Important negative scenarios include:

```text
publishing to /rosout
unsafe process package names
unsafe launch package names
unsafe rosbag names
path traversal attempts
```

These operations must be rejected before unsafe runtime execution occurs.

Examples of expected behavior:

```text
protected /rosout blocked: True

process traversal blocked: True

bag traversal blocked: True
```

---

# 56. Process Dry-Run Test

A process can be validated without starting it.

Example through the MCP interface:

```text
start_ros_process

package_name:
demo_nodes_cpp

executable:
talker

dry_run:
true
```

Expected resolution:

```text
package:
demo_nodes_cpp

executable:
talker

resolved_executable:
/opt/ros/jazzy/lib/demo_nodes_cpp/talker

dry_run:
true
```

No real process should be created.

---

# 57. Final Codex Read-Only Test

Start the required ROS test node in one terminal.

Start Codex in another:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
```

Example read-only verification prompt:

```text
Use only ros2_mcp.

Perform a read-only ROS 2 verification.

1. List the ROS 2 nodes.
2. List the ROS 2 topics.
3. List the ROS 2 actions.
4. Show the runtime health.
5. Show the active safety guardrails.

Do not use shell commands.
Do not modify files.
Do not use ros2_dev_mcp.
```

---

# 58. Final Action and Multi-Message Codex Test

Use:

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

At the end, show:
- which ros2_mcp tools were used
- whether the Fibonacci action was discovered
- its action type
- its server node
- the 5 received messages
- the selected QoS
- whether every operation succeeded
```

The verified tools are:

```text
list_actions
action_info
read_topic_messages
```

Expected result:

```text
Fibonacci discovered: Yes

type:
example_interfaces/action/Fibonacci

server:
/mcp_final_codex_server

messages:
5

QoS:
keep_last
depth 7
best_effort
volatile

every operation succeeded:
Yes
```

---

# 59. Final Repository Verification

Before committing Phase 7:

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

Review the Git status before staging.

Only intended Phase 7 files should be committed.

---

# 60. Final Commit Procedure

After the final documentation and tests:

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

The desired final state is:

```text
working tree clean
```

and:

```text
local main synchronized with origin/main
```

---

# 61. Phase 7 Final Result

Phase 7 transforms `ros2_mcp` into a broad generic ROS 2 runtime MCP layer.

The completed capabilities include:

```text
ROS graph discovery
ROS node inspection

topic discovery
topic inspection
single-message reading
multi-message reading
topic publishing

QoS configuration
QoS discovery
QoS recommendation
automatic QoS selection

persistent publishers

service discovery
service inspection
service calls

parameter discovery
parameter reading
parameter writing

action discovery
action inspection
one-shot action goals
managed action goals
action feedback
action result tracking
action cancellation

message interface discovery
service interface discovery
action interface discovery

ROS logging
diagnostics
runtime health

managed ROS processes
managed ROS launch files
ROS lifecycle operations

rosbag2 recording
rosbag2 playback

runtime safety guardrails
resource limits
dry-run support

executor serialization

modular ROS 2 Jazzy implementation
```

Final verified MCP tool count:

```text
46
```

Final verified unit/regression test count:

```text
11 passed
```

Final real Codex test:

```text
list_actions: PASSED
action_info: PASSED
read_topic_messages: PASSED
automatic QoS: PASSED
```

Earlier runtime problems found through integration testing were corrected:

```text
DiagnosticStatus integer conversion
    → FIXED

automatic QoS mismatch
    → FIXED

Executor is already spinning
    → FIXED

launch package resolution test
    → FIXED AND PASSED
```

The final architecture is modular rather than monolithic.

The generic ROS 2 runtime is now separated from future domain-specific MCP servers.

The planned architecture after Phase 7 is:

```text
                    AI / Codex / Agent
                           │
                           ▼
                       ros2_mcp
                           │
              Generic ROS 2 Runtime Layer
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
 ros2_control_mcp     ros2_nav_mcp    ros2_moveit_mcp
          │                │                │
          ▼                ▼                ▼
   ros2_control           Nav2            MoveIt 2

Additional specialized MCP components can later provide:

mcp_camera
LiDAR integrations
perception integrations
robot-specific integrations
```

`ros2_mcp` remains the generic ROS 2 foundation.

ROS 1 compatibility is intentionally not part of the project.

Camera/image retrieval is intentionally separated from the generic ROS runtime.

The next planned major implementation is:

```text
ros2_control_mcp
```

followed by:

```text
ros2_nav_mcp
ros2_moveit_mcp
```

After these runtime layers are available, the project can move toward real robot integrations using components such as:

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

Phase 7 is therefore the completed generic ROS 2 runtime foundation on which the specialized robotics MCP layers can be built.
