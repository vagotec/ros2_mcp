**# ROS 2 MCP**

A modular MCP server for inspecting, monitoring, and safely interacting with a running ROS 2 system.

\`ros2\_mcp\` focuses exclusively on ROS 2 runtime interaction.

ROS 2 project creation, package generation, build, and test workflows are provided separately by:

\`\`\`text
\`\`\`

The project currently targets:

\`\`\`text
ROS 2 Jazzy
Ubuntu 24.04
Python 3.12
rclpy
MCP Python SDK
\`\`\`

The current implementation exposes:

\`\`\`text
46 MCP runtime tools
\`\`\`

and has been verified through:

\`\`\`text
Python syntax checks
20 unit and integration tests
real ROS 2 Jazzy integration tests
direct MCP client tests
isolated wheel installation tests
installed MCP stdio tests
Codex end-to-end tests against source and installed packages
\`\`\`

Phase 8 additionally verifies that \`ros2\_mcp\` can be built, installed, configured, and started outside the source repository.

**---**

**# Goals**

The project provides a clean MCP interface to a running ROS 2 system.

Main goals:

\- Inspect the ROS 2 graph
\- Discover nodes, topics, services, actions, parameters, and interfaces
\- Read ROS 2 topic data
\- Read multiple topic messages
\- Inspect topic QoS
\- Automatically recommend compatible QoS
\- Publish structured ROS 2 messages
\- Maintain persistent publishers
\- Call ROS 2 services
\- Read and modify ROS 2 parameters
\- Discover and inspect ROS 2 Actions
\- Send ROS 2 Action goals
\- Receive ROS 2 Action feedback and results
\- Manage long-running Action goals
\- Cancel Action goals
\- Read \`/rosout\`
\- Read ROS diagnostics
\- Generate a runtime health summary
\- Start and stop managed ROS processes
\- Start and stop managed ROS launch files
\- Inspect and change lifecycle node states
\- Record and play rosbag2 data
\- Keep ROS-specific implementation details behind adapters
\- Keep ROS distributions replaceable
\- Keep MCP clients replaceable
\- Support Codex and other MCP-compatible clients
\- Keep runtime and development responsibilities separated
\- Avoid exposing arbitrary shell execution
\- Avoid exposing arbitrary ROS CLI execution
\- Apply configurable runtime safety guardrails
\- Keep subsystem-specific behavior outside the generic runtime MCP

**---**

**# Project Boundary**

\`ros2\_mcp\` is responsible for interacting with a running ROS 2 system.

Its responsibilities include:

\`\`\`text
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
\`\`\`

It does not create or modify ROS 2 software projects.

Development functionality belongs to:

\`\`\`text
\`\`\`

Examples include:

\`\`\`text
create workspace
create package
create node
create launch file
create parameter file
create tests
build project
run tests
\`\`\`

The separation is intentional.

\`\`\`text
Codex / MCP Client
        |
        +-------------------------+
        \|                         |
        v                         v
        \|                         |
        v                         v
 ROS 2 Runtime             ROS 2 Development
\`\`\`

This prevents runtime operations and filesystem/software-development operations from becoming coupled inside one MCP server.

**---**

**# Architecture**

The runtime architecture is layered.

\`\`\`text
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
\`\`\`

Current ROS distribution:

\`\`\`text
ROS 2 Jazzy
\`\`\`

The MCP and application layers do not directly depend on \`rclpy\`.

ROS distribution-specific behavior is isolated behind the ROS adapter layer.

This allows future ROS distribution adapters to be introduced without changing the MCP protocol-facing API.

**---**

**# Runtime Layer Responsibilities**

**## MCP Layer**

\`\`\`text
src/ros2\_mcp/mcp/runtime\_tools.py
\`\`\`

Responsibilities:

\`\`\`text
MCP tool definitions
structured MCP input
structured MCP output
tool annotations
delegation to RuntimeService
\`\`\`

The MCP layer does not directly use \`rclpy\`.

**---**

**## Application Layer**

\`\`\`text
src/ros2\_mcp/application/runtime/service.py
\`\`\`

Responsibilities:

\`\`\`text
runtime use cases
delegation through RosAdapter
ROS-independent application logic
\`\`\`

**---**

**## RosAdapter**

\`\`\`text
src/ros2\_mcp/ros/adapter.py
\`\`\`

Defines the abstract runtime contract.

The application layer depends on this abstraction instead of depending on the concrete Jazzy implementation.

**---**

**## ROS 2 Jazzy Adapter**

\`\`\`text
src/ros2\_mcp/ros/jazzy/
\`\`\`

Contains the concrete ROS 2 Jazzy implementation.

The implementation uses focused modules instead of one large monolithic adapter.

**---**

**# Modular ROS 2 Jazzy Architecture**

The original Jazzy adapter grew to more than 2,000 lines during runtime feature development.

It was therefore decomposed into dedicated modules.

Current structure:

\`\`\`text
src/ros2\_mcp/ros/jazzy/
├── actions.py
├── adapter.py
├── diagnostics.py
├── graph.py
├── \_\_init\_\_.py
├── interfaces.py
├── launches.py
├── lifecycle.py
├── logging.py
├── parameters.py
├── processes.py
├── publishers.py
├── qos.py
├── qos\_auto.py
├── rosbag.py
├── safety.py
├── services.py
└── topics.py
\`\`\`

The main:

\`\`\`text
adapter.py
\`\`\`

is now primarily responsible for:

\`\`\`text
ROS context initialization
runtime node creation
executor creation
executor synchronization
shared registries
mixin composition
cleanup
\`\`\`

ROS functionality lives in dedicated modules.

**---**

**# Jazzy Adapter Composition**

The concrete adapter composes the runtime features through mixins.

Conceptually:

\`\`\`text
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
\`\`\`

The complete abstract adapter contract has been verified.

Expected result:

\`\`\`text
Abstract methods: []
\`\`\`

**---**

**# Runtime Interaction Model**

The runtime MCP exposes explicit operations instead of arbitrary shell execution.

\`\`\`text
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
\`\`\`

The server does not expose:

\`\`\`text
arbitrary shell
arbitrary ros2 CLI
arbitrary Python execution
filesystem development operations
\`\`\`

This keeps runtime capabilities individually:

\`\`\`text
testable
documentable
restrictable
observable
\`\`\`

**---**

**# Current MCP Runtime Tools**

The final generic ROS 2 runtime MCP provides:

\`\`\`text
46 tools
\`\`\`

Current inventory:

\`\`\`text
action\_info
call\_service
cancel\_action\_goal
change\_lifecycle\_state
create\_persistent\_publisher
destroy\_persistent\_publisher
get\_action\_status
get\_bag\_info
get\_diagnostics
get\_lifecycle\_state
get\_parameter
get\_ros\_launch
get\_ros\_process
get\_runtime\_health
get\_safety\_guardrails
get\_topic\_qos
interface\_info
list\_actions
list\_interfaces
list\_nodes
list\_parameters
list\_persistent\_publishers
list\_ros\_launches
list\_ros\_processes
list\_services
list\_topics
node\_info
publish\_topic
publish\_with\_publisher
read\_rosout
read\_topic
read\_topic\_messages
recommend\_topic\_qos
send\_action\_goal
service\_info
set\_parameter
start\_action\_goal
start\_bag\_playback
start\_bag\_recording
start\_ros\_launch
start\_ros\_process
stop\_bag\_playback
stop\_bag\_recording
stop\_ros\_launch
stop\_ros\_process
topic\_info
\`\`\`

**---**

**# Runtime Capability Groups**

**## Graph and Discovery**

\`\`\`text
list\_nodes
list\_topics
topic\_info
node\_info
list\_services
service\_info
list\_parameters
get\_parameter
list\_interfaces
interface\_info
list\_actions
action\_info
\`\`\`

**---**

**## Topic Operations**

\`\`\`text
read\_topic
read\_topic\_messages
publish\_topic
get\_topic\_qos
recommend\_topic\_qos
\`\`\`

**---**

**## Persistent Publishers**

\`\`\`text
create\_persistent\_publisher
publish\_with\_publisher
list\_persistent\_publishers
destroy\_persistent\_publisher
\`\`\`

**---**

**## Services**

\`\`\`text
list\_services
service\_info
call\_service
\`\`\`

**---**

**## Parameters**

\`\`\`text
list\_parameters
get\_parameter
set\_parameter
\`\`\`

**---**

**## Actions**

\`\`\`text
list\_actions
action\_info
send\_action\_goal
start\_action\_goal
get\_action\_status
cancel\_action\_goal
\`\`\`

**---**

**## Runtime Observability**

\`\`\`text
read\_rosout
get\_diagnostics
get\_runtime\_health
\`\`\`

**---**

**## Interface Discovery**

\`\`\`text
list\_interfaces
interface\_info
\`\`\`

**---**

**## Process Management**

\`\`\`text
start\_ros\_process
get\_ros\_process
list\_ros\_processes
stop\_ros\_process
\`\`\`

**---**

**## Launch Management**

\`\`\`text
start\_ros\_launch
get\_ros\_launch
list\_ros\_launches
stop\_ros\_launch
\`\`\`

**---**

**## Lifecycle Management**

\`\`\`text
get\_lifecycle\_state
change\_lifecycle\_state
\`\`\`

**---**

**## rosbag2 Management**

\`\`\`text
start\_bag\_recording
stop\_bag\_recording
get\_bag\_info
start\_bag\_playback
stop\_bag\_playback
\`\`\`

**---**

**## Safety**

\`\`\`text
get\_safety\_guardrails
\`\`\`

**---**

**# ROS Graph Discovery**

**## \`list\_nodes\`**

Lists currently discovered ROS 2 nodes.

**---**

**## \`list\_topics\`**

Lists discovered topics and message types.

**---**

**## \`topic\_info\`**

Returns information such as:

\`\`\`text
topic name
topic types
publisher count
subscriber count
\`\`\`

**---**

**## \`node\_info\`**

Returns detailed node graph information.

This includes:

\`\`\`text
publishers
subscribers
service servers
service clients
\`\`\`

**---**

**## \`list\_services\`**

Lists discovered services and service types.

**---**

**## \`service\_info\`**

Returns information about a ROS 2 service and its runtime endpoints.

**---**

**# Topic Reading**

**## \`read\_topic\`**

Reads one ROS topic message.

The message type is dynamically discovered and resolved.

Example result:

\`\`\`json
{
  "topic": "/example",
  "type": "std\_msgs/msg/String",
  "message": {
    "data": "hello"
  }
}
\`\`\`

Topic reading uses automatic QoS discovery by default unless an explicit QoS profile is supplied.

**---**

**# Multi-Message Topic Reading**

**## \`read\_topic\_messages\`**

Collects multiple messages from a topic during a bounded observation period.

Important inputs:

\`\`\`text
topic\_name
max\_messages
duration\_sec
qos
\`\`\`

Example:

\`\`\`text
Topic:
/mcp\_final/multi\_messages

max\_messages:
5

duration\_sec:
2
\`\`\`

A real Codex test returned exactly five messages.

Example:

\`\`\`text
codex multi message 326
codex multi message 327
codex multi message 328
codex multi message 329
codex multi message 330
\`\`\`

The selected QoS was:

\`\`\`text
history: keep\_last
depth: 7
reliability: best\_effort
durability: volatile
\`\`\`

**---**

**# Topic Publishing**

**## \`publish\_topic\`**

Publishes one structured ROS message.

Example:

\`\`\`text
Topic:
/chatter

Type:
std\_msgs/msg/String
\`\`\`

Message:

\`\`\`json
{
  "data": "hello from ros2\_mcp"
}
\`\`\`

The message type is dynamically resolved.

Safety checks are applied before the write operation.

**---**

**# Persistent Publishers**

Phase 7 adds a managed publisher registry.

Tools:

\`\`\`text
create\_persistent\_publisher
publish\_with\_publisher
list\_persistent\_publishers
destroy\_persistent\_publisher
\`\`\`

The lifecycle is:

\`\`\`text
create\_persistent\_publisher
        |
        v
publisher\_id
        |
        +--> publish
        +--> publish
        +--> publish
        |
        v
destroy\_persistent\_publisher
\`\`\`

The registry stores information such as:

\`\`\`text
publisher\_id
topic
type
QoS
publish\_count
subscriber\_count
\`\`\`

A real subscriber successfully received multiple messages from the same persistent publisher.

**---**

**# QoS Support**

ROS 2 communication depends on DDS QoS compatibility.

Supported QoS properties include:

\`\`\`text
history
depth
reliability
durability
\`\`\`

Supported reliability values:

\`\`\`text
reliable
best\_effort
\`\`\`

Supported durability values:

\`\`\`text
volatile
transient\_local
\`\`\`

Supported history values:

\`\`\`text
keep\_last
keep\_all
\`\`\`

Invalid profiles are rejected.

**---**

**# QoS Inspection**

**## \`get\_topic\_qos\`**

Discovers QoS profiles used by current publishers and subscriptions.

Example:

\`\`\`text
history: keep\_last
depth: 7
reliability: best\_effort
durability: volatile
\`\`\`

**---**

**# QoS Recommendation**

**## \`recommend\_topic\_qos\`**

Generates a recommended profile for the requested role.

Example:

\`\`\`text
role:
subscription
\`\`\`

A BEST\_EFFORT publisher with depth 7 resulted in:

\`\`\`text
history: keep\_last
depth: 7
reliability: best\_effort
durability: volatile
\`\`\`

**---**

**# Automatic QoS Selection**

A real Codex integration test exposed an important QoS problem.

The publisher used:

\`\`\`text
BEST\_EFFORT
VOLATILE
KEEP\_LAST
depth 7
\`\`\`

The original default reader attempted:

\`\`\`text
RELIABLE
VOLATILE
KEEP\_LAST
depth 10
\`\`\`

ROS 2 reported:

\`\`\`text
incompatible QoS
Last incompatible policy: RELIABILITY
\`\`\`

The reader returned:

\`\`\`text
message: null
\`\`\`

The implementation was corrected so that topic reading automatically derives a compatible QoS profile when no explicit QoS configuration is supplied.

A real verification then returned:

\`\`\`json
{
  "message": {
    "data": "auto qos fixed 6"
  },
  "qos": {
    "history": "keep\_last",
    "depth": 7,
    "reliability": "best\_effort",
    "durability": "volatile"
  }
}
\`\`\`

Final result:

\`\`\`text
DEFAULT AUTO-QoS TEST: PASSED
\`\`\`

**---**

**# Service Calls**

**## \`call\_service\`**

Calls a ROS 2 service using structured input.

Example:

\`\`\`text
Service:
/mcp\_test/set\_enabled

Type:
std\_srvs/srv/SetBool
\`\`\`

Request:

\`\`\`json
{
  "data": true
}
\`\`\`

Verified response:

\`\`\`json
{
  "success": true,
  "message": "enabled"
}
\`\`\`

The service type is dynamically resolved.

**---**

**# Parameter Operations**

**## \`list\_parameters\`**

Lists parameters exposed by a ROS node.

**---**

**## \`get\_parameter\`**

Reads one parameter.

**---**

**## \`set\_parameter\`**

Changes one parameter.

Example:

\`\`\`text
Node:
/mcp\_parameter\_test

Parameter:
enabled

Value:
true
\`\`\`

Independent ROS 2 verification confirmed:

\`\`\`text
Boolean value is: True
\`\`\`

**---**

**# ROS Action Support**

The runtime supports both synchronous and managed action execution.

**---**

**## \`send\_action\_goal\`**

Sends a goal and waits for completion.

Example:

\`\`\`text
Action:
/mcp\_test/fibonacci

Type:
example\_interfaces/action/Fibonacci
\`\`\`

Goal:

\`\`\`json
{
  "order": 8
}
\`\`\`

Verified result:

\`\`\`json
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
\`\`\`

**---**

**# Action Discovery**

**## \`list\_actions\`**

Discovers active ROS 2 actions.

Verified example:

\`\`\`text
/mcp\_final/fibonacci
example\_interfaces/action/Fibonacci
\`\`\`

**---**

**# Action Inspection**

**## \`action\_info\`**

Returns structured information including:

\`\`\`text
name
types
server\_count
client\_count
servers
clients
transport endpoints
\`\`\`

Verified server:

\`\`\`text
/mcp\_final\_codex\_server
\`\`\`

The action transport includes endpoints such as:

\`\`\`text
\_action/send\_goal
\_action/get\_result
\_action/cancel\_goal
\_action/feedback
\_action/status
\`\`\`

**---**

**# Managed Action Goals**

Long-running actions can be managed across multiple MCP calls.

Tools:

\`\`\`text
start\_action\_goal
get\_action\_status
cancel\_action\_goal
\`\`\`

Conceptually:

\`\`\`text
start\_action\_goal
        |
        v
goal\_id
        |
        +--> get\_action\_status
        +--> get\_action\_status
        |
        v
cancel\_action\_goal
        |
        v
get\_action\_status
\`\`\`

Stored information includes:

\`\`\`text
goal\_id
action
type
goal
status
status\_name
feedback
result
completed
\`\`\`

A real test verified the action states:

\`\`\`text
EXECUTING
CANCELING
CANCELED
\`\`\`

**---**

**# Interface Discovery**

**## \`list\_interfaces\`**

Lists installed:

\`\`\`text
messages
services
actions
\`\`\`

Interfaces can be filtered by:

\`\`\`text
package
interface kind
\`\`\`

**---**

**## \`interface\_info\`**

Returns structured interface information.

Example message:

\`\`\`text
std\_msgs/msg/String
\`\`\`

Result:

\`\`\`text
kind: msg

fields:
data: string
\`\`\`

Example service:

\`\`\`text
std\_srvs/srv/SetBool
\`\`\`

Result contains:

\`\`\`text
request
response
\`\`\`

Example action:

\`\`\`text
example\_interfaces/action/Fibonacci
\`\`\`

Result contains:

\`\`\`text
goal
result
feedback
\`\`\`

**---**

**# ROS Logging**

**## \`read\_rosout\`**

Reads structured ROS log messages from:

\`\`\`text
/rosout
\`\`\`

Filtering supports:

\`\`\`text
node
minimum severity
maximum number of messages
\`\`\`

Example verified ERROR messages:

\`\`\`text
codex rosout error 14
codex rosout error 15
codex rosout error 16
codex rosout error 17
codex rosout error 18
codex rosout error 19
\`\`\`

Codex successfully retrieved the log entries using only \`ros2\_mcp\`.

**---**

**# Diagnostics**

**## \`get\_diagnostics\`**

Reads ROS diagnostics from:

\`\`\`text
/diagnostics
\`\`\`

using:

\`\`\`text
diagnostic\_msgs/msg/DiagnosticArray
\`\`\`

Supported levels:

\`\`\`text
OK
WARN
ERROR
STALE
\`\`\`

A ROS 2 Jazzy compatibility issue involving the generated Python representation of \`DiagnosticStatus.level\` was discovered during real testing and corrected.

**---**

**# Runtime Health**

**## \`get\_runtime\_health\`**

Combines:

\`\`\`text
ROS graph
diagnostics
rosout
\`\`\`

into one compact runtime health summary.

Example:

\`\`\`text
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
\`\`\`

Possible overall states include:

\`\`\`text
OK
WARN
ERROR
\`\`\`

**---**

**# Executor Serialization**

A real Codex test exposed concurrent executor access.

Observed error:

\`\`\`text
Executor is already spinning
\`\`\`

Multiple MCP requests were attempting to spin the shared ROS executor concurrently.

The Jazzy adapter now serializes executor access using a shared lock.

Executor operations are centralized through adapter helper methods.

A concurrent verification executed:

\`\`\`text
get\_runtime\_health
list\_nodes
list\_topics
get\_runtime\_health
\`\`\`

successfully.

Final result:

\`\`\`text
CONCURRENT EXECUTOR TEST: PASSED
\`\`\`

**---**

**# ROS Process Management**

Tools:

\`\`\`text
start\_ros\_process
get\_ros\_process
list\_ros\_processes
stop\_ros\_process
\`\`\`

Processes are resolved through ROS package information.

The runtime does not expose arbitrary shell execution.

Dry-run example:

\`\`\`text
package:
demo\_nodes\_cpp

executable:
talker
\`\`\`

Resolved executable:

\`\`\`text
/opt/ros/jazzy/lib/demo\_nodes\_cpp/talker
\`\`\`

Result:

\`\`\`text
dry\_run: true
\`\`\`

**---**

**# ROS Launch Management**

Tools:

\`\`\`text
start\_ros\_launch
get\_ros\_launch
list\_ros\_launches
stop\_ros\_launch
\`\`\`

Launch files are resolved through installed ROS packages and the ament index.

A real test package was registered temporarily and used to start:

\`\`\`text
mcp\_launch\_test\_talker
\`\`\`

The full lifecycle passed:

\`\`\`text
START
GET
LIST
STOP
LIST AFTER STOP
\`\`\`

Final result:

\`\`\`text
REAL LAUNCH MANAGEMENT TEST: PASSED
\`\`\`

**---**

**# Lifecycle Node Management**

Tools:

\`\`\`text
get\_lifecycle\_state
change\_lifecycle\_state
\`\`\`

Verified transitions included:

\`\`\`text
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
\`\`\`

The lifecycle test successfully performed:

\`\`\`text
configure
activate
deactivate
cleanup
\`\`\`

**---**

**# rosbag2 Management**

Recording tools:

\`\`\`text
start\_bag\_recording
stop\_bag\_recording
get\_bag\_info
\`\`\`

Playback tools:

\`\`\`text
start\_bag\_playback
stop\_bag\_playback
\`\`\`

A real recording test captured messages from:

\`\`\`text
/mcp\_bag\_test
\`\`\`

The recorded bag was inspected and subsequently played back.

Managed bag names are validated by the safety layer.

Dry-run mode is also available.

**---**

**# Safety Model**

Phase 7 introduces explicit runtime guardrails.

Safety implementation:

\`\`\`text
src/ros2\_mcp/ros/jazzy/safety.py
\`\`\`

Packaged default configuration:

\`\`\`text
src/ros2\_mcp/config/default.toml
\`\`\`

Configuration loader and resolver:

\`\`\`text
src/ros2\_mcp/config/settings.py
\`\`\`

Optional external deployment configuration can be selected with:

\`\`\`text
ROS2\_MCP\_CONFIG
\`\`\`

The repository-level:

\`\`\`text
config/ros2\_mcp.toml
\`\`\`

can still be used as an explicit external configuration, but runtime code no longer depends on the current working directory to find it.

**---**

**# No Arbitrary Shell**

The active policy reports:

\`\`\`text
arbitrary\_shell: false
\`\`\`

The runtime exposes explicit ROS operations instead of shell commands.

**---**

**# Managed Stop Policies**

Safety reports:

\`\`\`text
managed\_process\_stop\_only: true
managed\_launch\_stop\_only: true
managed\_rosbag\_stop\_only: true
\`\`\`

Only resources managed by this MCP server can be stopped through these operations.

**---**

**# Package and Launch Resolution**

Safety reports:

\`\`\`text
package\_resolution\_required: true
launch\_file\_resolution\_required: true
\`\`\`

Managed process and launch execution must resolve through ROS package infrastructure.

**---**

**# Path Traversal Protection**

Unsafe resource names are rejected.

Examples:

\`\`\`text
../bad
\`\`\`

Negative tests verified:

\`\`\`text
process traversal blocked: True
bag traversal blocked: True
\`\`\`

**---**

**# Structured Argument Validation**

Process arguments are passed as structured lists instead of shell strings.

Validation rejects:

\`\`\`text
NUL characters
newlines
carriage returns
oversized arguments
excessive argument counts
\`\`\`

**---**

**# Protected ROS Topics**

Current protected topics include:

\`\`\`text
/parameter\_events
/rosout
\`\`\`

Writing directly to these topics is blocked.

Verified result:

\`\`\`text
protected /rosout blocked: True
\`\`\`

**---**

**# Configurable Safety Policies**

Configuration supports:

\`\`\`text
protected\_topics
protected\_services
protected\_parameters
protected\_actions

allowed\_process\_packages
allowed\_launch\_packages
\`\`\`

This allows installations to apply tighter policies without changing the implementation.

**---**

**# Runtime Resource Limits**

Current configured limits include:

\`\`\`text
persistent\_publishers: 32
managed\_processes: 16
managed\_launches: 8
bag\_recordings: 4
bag\_playbacks: 4
\`\`\`

These limits prevent unbounded resource creation.

**---**

**# Dry-Run Support**

Dry-run mode is available for:

\`\`\`text
start\_ros\_process
start\_ros\_launch
start\_bag\_recording
start\_bag\_playback
\`\`\`

This allows an MCP client to validate an operation before actually starting a runtime resource.

**---**

**# Safety Inspection**

**## \`get\_safety\_guardrails\`**

Returns the active runtime safety configuration.

Important information includes:

\`\`\`text
shell policy
managed stop policy
protected resources
allowed packages
resource limits
dry-run support
\`\`\`

**---**

**# Phase 8 Packaging and Deployment Readiness**

Phase 8 verifies that \`ros2\_mcp\` is no longer dependent on execution from the source repository.

The validated deployment path is:

\`\`\`text
source tree
    |
    v
uv build
    |
    v
wheel
    |
    v
isolated virtual environment
    |
    v
installed ros2-mcp CLI
    |
    v
packaged default.toml
    |
    v
MCP stdio
    |
    v
Codex / MCP Client
    |
    v
ROS 2 Jazzy
\`\`\`

Verified Phase 8 properties:

\`\`\`text
centralized configuration resolution
packaged default configuration
ROS2\_MCP\_CONFIG override
invalid explicit configuration rejection
wheel and sdist build
isolated wheel installation
execution outside repository
installed CLI verification
real installed MCP stdio
46-tool inventory after installation
installed safety configuration
installed runtime health
Codex verification against installed package
20 permanent tests
\`\`\`

**---**

**# Configuration Resolution**

Configuration lookup is centralized in:

\`\`\`text
src/ros2\_mcp/config/settings.py
\`\`\`

The precedence is:

\`\`\`text
explicit configuration path
            |
            v
     ROS2\_MCP\_CONFIG
            |
            v
  packaged default.toml
\`\`\`

The packaged default is:

\`\`\`text
src/ros2\_mcp/config/default.toml
\`\`\`

An explicitly configured file must exist.

Invalid explicit configuration does not silently fall back to the packaged default.

Example external configuration:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS2\_MCP\_CONFIG="$PWD/config/ros2\_mcp.toml"

ros2-mcp
\`\`\`

**---**

**# Build Distribution Packages**

The project uses \`uv\_build\`.

Build wheel and source distribution:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf dist

uv build

find dist \\
  -maxdepth 1 \\
  -type f \\
  -printf '%f\n' \\
  \| sort
\`\`\`

Expected artifacts:

\`\`\`text
\*.whl
\*.tar.gz
\`\`\`

The wheel contains:

\`\`\`text
ros2\_mcp/config/default.toml
\`\`\`

**---**

**# Isolated Wheel Installation**

A clean virtual environment can verify installation independently of the source checkout.

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf /tmp/ros2\_mcp\_phase\_8\_test\_venv

python -m venv \\
  \--system-site-packages \\
  /tmp/ros2\_mcp\_phase\_8\_test\_venv

/tmp/ros2\_mcp\_phase\_8\_test\_venv/bin/pip install \\
  dist/\*.whl
\`\`\`

\`--system-site-packages\` allows the isolated Python environment to access the ROS 2 Jazzy Python installation, including \`rclpy\`.

Verify the installed package from outside the repository:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

cd /tmp

/tmp/ros2\_mcp\_phase\_8\_test\_venv/bin/python - <<'PY'
import ros2\_mcp
import rclpy

from ros2\_mcp.config.settings import (
    load\_settings,
    resolve\_config\_path,
)

config\_path = resolve\_config\_path()

print("ros2\_mcp:", ros2\_mcp.\_\_file\_\_)
print("rclpy:", rclpy.\_\_file\_\_)
print("config:", config\_path)
print("settings:", load\_settings(config\_path))
PY

cd \~/projects/robotics/ros2\_mcp
\`\`\`

The configuration path must resolve into the installed package rather than the project repository.

**---**

**# Installed MCP stdio Verification**

The installed package was verified through the real MCP stdio protocol.

Expected installed tool inventory:

\`\`\`text
46 tools
\`\`\`

Representative installed operations verified:

\`\`\`text
list\_nodes
list\_topics
list\_actions
interface\_info
list\_interfaces
get\_runtime\_health
get\_safety\_guardrails
start\_ros\_process with dry\_run=true
\`\`\`

The installed server can execute from \`/tmp\` and does not require the source repository as its working directory.

**---**

**# Permanent Phase 8 Tests**

Phase 8 adds:

\`\`\`text
tests/unit/test\_settings.py
tests/integration/test\_server\_lifespan.py
\`\`\`

Configuration tests verify:

\`\`\`text
packaged default resolution
explicit configuration precedence
ROS2\_MCP\_CONFIG override
missing explicit configuration rejection
missing environment configuration rejection
default settings loading
custom settings loading
invalid positive-limit validation
\`\`\`

The server lifespan integration test verifies:

\`\`\`text
create\_server
configuration loading
runtime initialization
46 MCP tools
get\_safety\_guardrails
get\_runtime\_health
start\_ros\_process with dry\_run=true
clean shutdown
\`\`\`

Final Phase 8 test count:

\`\`\`text
20 passed
\`\`\`

**---**

**# Development Environment**

Current development environment:

\`\`\`text
Ubuntu 24.04
ROS 2 Jazzy
Python 3.12
uv
MCP Python SDK
Cyclone DDS
\`\`\`

**---**

**# Environment Setup**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
\`\`\`

When explicitly configuring the project ROS domain:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS\_DOMAIN\_ID=30
export RMW\_IMPLEMENTATION=rmw\_cyclonedds\_cpp
\`\`\`

**---**

**# Install Dependencies**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp

uv sync
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
\`\`\`

**---**

**# Run the MCP Server**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m ros2\_mcp.server
\`\`\`

The server uses MCP standard I/O transport.

**---**

**# Syntax Check**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
\`\`\`

Expected:

\`\`\`text
exit code 0
\`\`\`

**---**

**# Runtime Tests**

Run:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q
\`\`\`

Final verified Phase 8 result:

\`\`\`text
....................                                                     [100%]

20 passed
\`\`\`

**---**

**# Complete Local Verification**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
\`\`\`

Expected:

\`\`\`text
20 passed
\`\`\`

**---**

**# MCP Tool Inventory Test**

The registered MCP tools can be queried directly.

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import asyncio

from mcp import Client
from ros2\_mcp.server import create\_server


async def main() -> None:
    """Print all registered ros2\_mcp tools."""
    server = create\_server()

    async with Client(
        server,
        raise\_exceptions=True,
    ) as client:
        result = await client.list\_tools()

        names = sorted(
            tool.name
            for tool in result.tools
        )

        print("Tool count:", len(names))

        for name in names:
            print(name)


asyncio.run(main())
PY
\`\`\`

Expected final result:

\`\`\`text
Tool count: 46
\`\`\`

**---**

**# Adapter Contract Check**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from ros2\_mcp.ros.jazzy.adapter import JazzyRosAdapter


print(
    "Abstract methods:",
    sorted(JazzyRosAdapter.\_\_abstractmethods\_\_),
)

if JazzyRosAdapter.\_\_abstractmethods\_\_:
    raise RuntimeError(
        "JazzyRosAdapter does not implement the complete RosAdapter contract."
    )

print("JazzyRosAdapter contract: OK")
PY
\`\`\`

Expected:

\`\`\`text
Abstract methods: []
JazzyRosAdapter contract: OK
\`\`\`

**---**

**# Adapter Structure Check**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

wc -l src/ros2\_mcp/ros/jazzy/adapter.py

find src/ros2\_mcp/ros/jazzy \\
  -maxdepth 1 \\
  -type f \\
  -printf '%f\n' \\
  \| sort
\`\`\`

The implementation should remain modular.

**---**

**# Safety Guardrail Check**

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from pprint import pprint

from ros2\_mcp.ros.jazzy.adapter import JazzyRosAdapter


adapter = JazzyRosAdapter()
try:
    pprint(
        adapter.get\_safety\_guardrails()
    )
finally:
    adapter.close()
PY
\`\`\`

**---**

**# Codex Integration**

Register the local MCP server with Codex.

Example:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp add ros2\_mcp \\
  \--env ROS\_DOMAIN\_ID=30 \\
  \--env RMW\_IMPLEMENTATION=rmw\_cyclonedds\_cpp \\
  \-- \\
  bash -lc 'cd /home/sarvg/projects/robotics/ros2\_mcp && source /opt/ros/jazzy/setup.bash && source .venv/bin/activate && exec python -m ros2\_mcp.server'
\`\`\`

Inspect the registration:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2\_mcp
\`\`\`

Start Codex:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
\`\`\`

Inside Codex:

\`\`\`text
/mcp
\`\`\`

**---**

**# Codex Installed-Package Verification**

Phase 8 also verifies Codex against an isolated installed wheel.

A temporary MCP registration can be created without replacing the development registration:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp remove ros2\_mcp\_installed 2>/dev/null || true

codex mcp add ros2\_mcp\_installed \\
  \--env ROS\_DOMAIN\_ID=30 \\
  \--env RMW\_IMPLEMENTATION=rmw\_cyclonedds\_cpp \\
  \-- \\
  bash -lc \\
  'source /opt/ros/jazzy/setup.bash && exec /tmp/ros2\_mcp\_phase\_8\_3\_final\_venv/bin/ros2-mcp'

codex mcp get ros2\_mcp\_installed
codex mcp list
\`\`\`

Start Codex:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
\`\`\`

The final installed-package verification used only:

\`\`\`text
ros2\_mcp\_installed
\`\`\`

and successfully exercised:

\`\`\`text
list\_nodes
list\_topics
list\_actions
interface\_info
list\_interfaces
get\_runtime\_health
get\_safety\_guardrails
start\_ros\_process with dry\_run=true
\`\`\`

Final result:

\`\`\`text
all requested operations succeeded
no real ROS process started
no project file modified
\`\`\`

The temporary verification registration can be removed afterwards:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp remove ros2\_mcp\_installed
codex mcp list
\`\`\`

The \`/tmp\` installation is a test environment only and is not intended as a permanent deployment location.

**---**

**# Codex Usage Rule**

For runtime-only tests, Codex can be explicitly instructed:

\`\`\`text
Use only ros2\_mcp.
Do not use shell commands.
Do not modify files.
\`\`\`

This makes it possible to verify that Codex selects the runtime MCP instead of falling back to the shell or development server.

**---**

**# Verified Codex Runtime Operations**

Codex has successfully exercised runtime operations including:

\`\`\`text
list\_nodes
topic\_info
publish\_topic
call\_service
set\_parameter
send\_action\_goal
read\_rosout
interface\_info
list\_interfaces
get\_topic\_qos
recommend\_topic\_qos
get\_runtime\_health
get\_safety\_guardrails
start\_ros\_process with dry\_run
list\_actions
action\_info
read\_topic\_messages
\`\`\`

**---**

**# Final Codex Action and Multi-Message Test**

A final integration environment exposed:

\`\`\`text
Action:
/mcp\_final/fibonacci

Action type:
example\_interfaces/action/Fibonacci

Server:
/mcp\_final\_codex\_server
\`\`\`

and:

\`\`\`text
Topic:
/mcp\_final/multi\_messages
\`\`\`

Codex was instructed:

\`\`\`text
Use only ros2\_mcp.
Perform the final verification of the three new ROS 2 core tools.

1\. List all currently discovered ROS 2 actions.

2\. Inspect this action:
   /mcp\_final/fibonacci

3\. Read exactly 5 messages from:
   /mcp\_final/multi\_messages

Use automatic QoS selection.
Use a maximum duration of 2 seconds.

Do not use shell commands.
Do not modify files.
\`\`\`

Codex selected:

\`\`\`text
list\_actions
action\_info
read\_topic\_messages
\`\`\`

All operations succeeded.

Five messages were received:

\`\`\`text
codex multi message 326
codex multi message 327
codex multi message 328
codex multi message 329
codex multi message 330
\`\`\`

QoS:

\`\`\`text
history: keep\_last
depth: 7
reliability: best\_effort
durability: volatile
\`\`\`

Final Codex result:

\`\`\`text
Every operation succeeded: Yes
\`\`\`

**---**

**# Real ROS 2 Verification**

The implementation has been tested against a real ROS 2 Jazzy runtime.

Verified areas include:

\`\`\`text
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
\`\`\`

**---**

**# Important Runtime Issues Found and Fixed**

Real runtime testing exposed several issues that unit testing alone did not reveal.

**## Diagnostic Level Representation**

ROS diagnostic severity values required normalization before integer comparison.

Status:

\`\`\`text
FIXED
\`\`\`

**---**

**## Auto-QoS Compatibility**

A RELIABLE subscription could not receive from a BEST\_EFFORT publisher.

Status:

\`\`\`text
FIXED
\`\`\`

Default topic reading now automatically derives a compatible profile.

**---**

**## Executor Concurrency**

Concurrent MCP calls produced:

\`\`\`text
Executor is already spinning
\`\`\`

Status:

\`\`\`text
FIXED
\`\`\`

Executor access is now serialized.

**---**

**## Launch Package Resolution**

The launch integration test initially used an incomplete temporary ament package registration.

The test environment was corrected to use the ament resource index.

Status:

\`\`\`text
FIXED
REAL LAUNCH MANAGEMENT TEST: PASSED
\`\`\`

**---**

**# Documentation**

Runtime development documentation is stored in:

\`\`\`text
docs/
├── README\_PHASE\_1.md
├── README\_PHASE\_2.md
├── README\_PHASE\_3.md
├── README\_PHASE\_4.md
├── README\_PHASE\_5.md
├── README\_PHASE\_6.md
├── README\_PHASE\_7.md
└── README\_PHASE\_8.md
\`\`\`

Phase 6 documents the controlled interaction foundation.

Phase 7 documents the advanced runtime, observability, safety, management, QoS, modularization, and final integration work.

Phase 8 documents configuration resolution, packaged defaults, wheel installation, installed MCP stdio operation, Codex verification against the installed package, and permanent packaging/configuration regression tests.

**---**

**# Completed Runtime Capabilities**

\`\`\`text
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
Installed-package Codex test   ✅
Runtime / Dev separation       ✅
Real ROS 2 verification        ✅

Central config resolution      ✅
Packaged default config        ✅
Wheel + sdist build            ✅
Isolated wheel installation    ✅
Installed MCP stdio            ✅
Server lifespan regression     ✅
\`\`\`

**---**

**# Verified Final Status**

\`\`\`text
MCP tools:
46

Unit/integration/regression tests:
20 passed

Python syntax:
PASS

Real ROS 2 integration:
PASS

Wheel build:
PASS

Isolated wheel installation:
PASS

Installed MCP stdio:
PASS

Packaged default configuration:
PASS

Codex source integration:
PASS

Codex installed-package integration:
PASS
\`\`\`

**---**

**# Current Limitations and Intentional Boundaries**

The following capabilities are intentionally outside the generic \`ros2\_mcp\` scope:

\`\`\`text
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

ros2\_control-specific semantics
Nav2-specific semantics
MoveIt 2-specific semantics

robot-specific physical safety
controller-specific safety
navigation-specific safety
manipulation-specific safety
\`\`\`

These are not considered missing generic runtime features.

They belong to separate development or specialized robotics MCP servers.

**---**

**# Image Retrieval Boundary**

Camera and image retrieval are intentionally not implemented directly in \`ros2\_mcp\`.

A future specialized MCP can provide:

\`\`\`text
mcp\_camera
\`\`\`

Possible responsibilities:

\`\`\`text
image retrieval
depth images
camera info
camera configuration
stream selection
camera metadata
point-cloud conversion
camera-specific diagnostics
\`\`\`

Possible future hardware:

\`\`\`text
Intel RealSense
Luxonis OAK-D
Stereolabs ZED2
generic ROS image\_transport cameras
\`\`\`

\`ros2\_mcp\` can still inspect the corresponding ROS topics through its normal graph and topic tools.

**---**

**# ROS 1 Boundary**

This project targets ROS 2.

ROS 1 is intentionally not supported.

The architecture is built around:

\`\`\`text
ROS 2
DDS
rclpy
ROS 2 Actions
ROS 2 Lifecycle
ROS 2 QoS
ROS 2 interfaces
\`\`\`

ROS 1 compatibility would require a separate runtime model and is outside the project scope.

**---**

**# Specialized MCP Architecture**

The generic runtime MCP should remain focused.

Future subsystem-specific servers can build on the generic ROS 2 runtime foundation.

\`\`\`text
                    MCP Client / AI Agent
                            |
            +---------------+---------------+
            \|               |               |
            v               v               v
            \|               |               |
            v               v               |
      ROS 2 Runtime     ROS 2 Projects       |
                                            +--> ros2\_control\_mcp
                                            +--> ros2\_nav\_mcp
                                            +--> ros2\_moveit\_mcp
                                            +--> mcp\_camera
\`\`\`

**---**

**# ros2\_control MCP**

Planned:

\`\`\`text
ros2\_control\_mcp
\`\`\`

Possible responsibilities:

\`\`\`text
controller manager
controller states
controller switching
hardware interfaces
resource claims
joint command interfaces
joint state interfaces
hardware status
controller safety
\`\`\`

These concepts should not be embedded directly into generic \`ros2\_mcp\`.

**---**

**# Nav2 MCP**

Planned:

\`\`\`text
ros2\_nav\_mcp
\`\`\`

Possible responsibilities:

\`\`\`text
navigation goals
navigation cancellation
navigation status
maps
costmaps
localization
planner selection
behavior trees
navigation safety
\`\`\`

Generic Action and Lifecycle functionality from \`ros2\_mcp\` provides the runtime foundation.

**---**

**# MoveIt 2 MCP**

Planned:

\`\`\`text
ros2\_moveit\_mcp
\`\`\`

Possible responsibilities:

\`\`\`text
planning groups
robot state
joint targets
pose targets
motion planning
trajectory execution
planning scene
collision objects
manipulation safety
\`\`\`

The generic ROS topic, service, parameter, action, and interface tools remain in \`ros2\_mcp\`.

**---**

**# Camera MCP**

Planned:

\`\`\`text
mcp\_camera
\`\`\`

Possible responsibilities:

\`\`\`text
image retrieval
depth retrieval
camera info
stream management
camera configuration
camera-specific diagnostics
camera point-cloud handling
\`\`\`

This separation prevents the generic ROS runtime server from becoming monolithic.

**---**

**# Future Real Robot Integration**

Once the specialized MCP servers are available, realistic robot scenarios can be built.

Examples include:

\`\`\`text
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
\`\`\`

Conceptually:

\`\`\`text
LLM / MCP Client
        |
        v
Specialized MCP
        |
        v
ros2\_mcp Runtime Foundation
        |
        v
ROS 2
        |
        v
Robot / Sensors / Actuators
\`\`\`

**---**

**# Project Principles**

\- Runtime and development tooling remain separated
\- ROS access goes through a dedicated adapter
\- ROS distributions should remain replaceable
\- MCP clients should remain replaceable
\- Read and write operations remain clearly distinguishable
\- Runtime write operations are explicit
\- Avoid private or unstable ROS APIs when possible
\- Avoid unnecessary frameworks
\- No arbitrary shell interface in the runtime MCP
\- No arbitrary ROS CLI execution in the runtime MCP
\- Safety policies remain explicit and inspectable
\- Runtime resources remain managed and bounded
\- Subsystem-specific semantics remain separate
\- Implementation remains independent
\- External ROS MCP projects may be evaluated for architecture and feature comparison
\- External ROS MCP code is not copied into this implementation

**---**

**# Current Project Status**

\`\`\`text
Phase 1   Runtime foundation                   ✅
Phase 2   ROS graph discovery                  ✅
Phase 3   Topic runtime inspection             ✅
Phase 4   Runtime architecture expansion       ✅
Phase 5   Extended runtime inspection          ✅
Phase 6   Controlled runtime interaction       ✅
Phase 7   Advanced runtime operations          ✅
Phase 8   Packaging and deployment readiness   ✅
\`\`\`

The generic ROS 2 runtime foundation is now operational.

Final generic runtime status:

\`\`\`text
46 MCP tools
20 tests passed
real ROS 2 verification passed
wheel and sdist build passed
isolated wheel installation passed
installed MCP stdio verification passed
Codex source verification passed
Codex installed-package verification passed
packaged default configuration enabled
centralized configuration resolution enabled
modular Jazzy architecture
safety guardrails enabled
\`\`\`

The generic \`ros2\_mcp\` feature scope is therefore considered complete for the current architecture.

**---**

**# Final Repository Verification**

Before committing:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
pytest --collect-only -q
git diff --check

git status
git diff --stat
\`\`\`

Expected:

\`\`\`text
20 passed
\`\`\`

**---**

**# Final Commit Procedure**

After documentation and final verification:

\`\`\`bash
cd \~/projects/robotics/ros2\_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git status
git diff --stat

git add \\
  README.md \\
  docs/README\_PHASE\_8.md \\
  src/ros2\_mcp/config/default.toml \\
  src/ros2\_mcp/config/settings.py \\
  src/ros2\_mcp/ros/jazzy/safety.py \\
  src/ros2\_mcp/server.py \\
  tests/integration/test\_server\_lifespan.py \\
  tests/unit/test\_settings.py

git status --short

git commit -m "feat: complete ROS 2 MCP packaging and deployment phase 8"

git push origin main

git status
git log --oneline -5
\`\`\`

Desired final state:

\`\`\`text
working tree clean
branch synchronized with origin/main
\`\`\`

**---**

**# Repository**

This project is developed independently.

Other ROS MCP implementations may be evaluated for feature and architecture comparison, but their source code is not used as a copy-and-paste implementation basis.

The architecture and implementation of \`ros2\_mcp\` are developed specifically for this project.
