# Phase 6 – Controlled ROS 2 Runtime Interaction

## Goal

Phase 6 extends `ros2_mcp` from read-only ROS 2 runtime inspection to controlled runtime interaction.

The previous runtime phases established the ability to inspect a running ROS 2 system through MCP tools.

Phase 6 introduces carefully selected write operations while preserving the existing layered architecture and keeping ROS-specific implementation details outside the MCP layer.

The first write operation implemented in Phase 6 is:

```text
publish_topic
```

This allows an MCP-compatible client such as Codex to publish a single ROS 2 message without using shell commands or accessing ROS 2 directly.

Phase 6 is intentionally implemented incrementally.

Planned runtime interaction capabilities include:

```text
publish_topic
call_service
set_parameter
```

Additional controlled runtime capabilities may be introduced later after the core write operations are stable.

---

## Project Boundary

`ros2_mcp` is responsible for interaction with a running ROS 2 system.

It is not responsible for ROS 2 project creation or software development workflows.

The project boundary is:

```text
ros2_mcp
    |
    +--> runtime inspection
    +--> runtime monitoring
    +--> controlled runtime interaction
```

ROS 2 software development operations belong to the separate project:

```text
ros2_dev_mcp
```

That project handles operations such as:

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

This separation keeps runtime operations independent from filesystem and development operations.

---

## Architecture

Phase 6 continues to use the existing layered runtime architecture.

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
rclpy
    |
    v
ROS 2 / DDS
```

For example, a topic publication follows this path:

```text
Codex
    |
    v
ros2_mcp.publish_topic
    |
    v
RuntimeService.publish_topic
    |
    v
RosAdapter.publish_topic
    |
    v
JazzyRosAdapter.publish_topic
    |
    v
rclpy Publisher
    |
    v
ROS 2 / DDS
    |
    v
Topic Subscriber
```

The MCP layer does not access `rclpy` directly.

The application service does not implement ROS-specific behavior.

ROS-specific runtime interaction remains behind the `RosAdapter` abstraction.

---

## Design Principles

### Separation of Concerns

Each layer has a specific responsibility.

```text
MCP layer
    Protocol-facing tool definitions

Application layer
    Runtime use cases

ROS adapter interface
    Runtime abstraction boundary

Jazzy adapter
    ROS 2 Jazzy implementation

rclpy
    ROS 2 Python client library
```

This prevents MCP protocol code from becoming tightly coupled to ROS 2 implementation details.

### Runtime-Only Responsibility

`ros2_mcp` interacts with running ROS 2 systems.

It does not create or modify ROS 2 source projects.

Filesystem-based project creation belongs to:

```text
ros2_dev_mcp
```

### Controlled Write Operations

Phase 6 does not introduce unrestricted ROS 2 command execution.

Instead, individual runtime operations are exposed explicitly as MCP tools.

The MCP client is not given an arbitrary shell or ROS CLI execution interface.

The preferred model is:

```text
MCP Client
    |
    v
Explicit MCP Tool
    |
    v
Validated Structured Input
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

---

# Step 1 – Topic Publishing

## Overview

The first controlled write capability introduced in Phase 6 is:

```text
publish_topic
```

The tool publishes one message to a ROS 2 topic.

The operation requires:

```text
topic_name
message_type
message
```

Example:

```text
topic_name   = /chatter
message_type = std_msgs/msg/String
message      = {"data": "hello from ros2_mcp"}
```

---

## MCP Tool

The MCP-facing operation is:

```text
publish_topic
```

Conceptually, the tool accepts:

```python
publish_topic(
    topic_name: str,
    message_type: str,
    message: dict[str, object],
)
```

Example MCP input:

```json
{
  "topic_name": "/chatter",
  "message_type": "std_msgs/msg/String",
  "message": {
    "data": "hello from ros2_mcp"
  }
}
```

Example result:

```json
{
  "topic": "/chatter",
  "type": "std_msgs/msg/String",
  "message": {
    "data": "hello from ros2_mcp"
  },
  "subscriber_count": 1,
  "published": true
}
```

---

## Tool Annotations

`publish_topic` is a write operation.

Its MCP annotations describe it as:

```text
read_only_hint   = false
destructive_hint = false
idempotent_hint  = false
open_world_hint  = false
```

### `read_only_hint = false`

Publishing changes the observable ROS 2 runtime state by sending a message.

Therefore the operation is not read-only.

### `destructive_hint = false`

The operation publishes a message but does not inherently delete ROS 2 resources.

The semantic effect of the published message still depends on the target topic and receiving system.

### `idempotent_hint = false`

Publishing the same message multiple times can produce repeated effects.

Therefore publication must not be treated as idempotent.

### `open_world_hint = false`

The operation interacts with the configured ROS 2 runtime rather than an unrestricted external system.

---

## RosAdapter Interface

The generic ROS adapter defines the operation independently from ROS 2 Jazzy implementation details.

The interface is:

```python
def publish_topic(
    self,
    topic_name: str,
    message_type: str,
    message: dict[str, object],
) -> dict[str, object]:
    """Publish one message to a ROS topic."""
```

This maintains the adapter boundary.

The application and MCP layers do not need to know how publishers are created or how ROS message classes are resolved.

---

## RuntimeService

`RuntimeService` exposes the publication use case to the MCP layer.

Conceptually:

```python
def publish_topic(
    self,
    topic_name: str,
    message_type: str,
    message: dict[str, object],
) -> dict[str, object]:
    """Publish one message to a ROS topic."""
```

The service delegates the operation to the configured ROS adapter.

The service does not import or use `rclpy`.

---

## JazzyRosAdapter

The ROS 2 Jazzy implementation performs the actual publication.

The implementation follows this sequence:

```text
normalize topic name
        |
        v
validate message type
        |
        v
resolve ROS message class
        |
        v
create ROS message instance
        |
        v
populate message fields
        |
        v
create temporary publisher
        |
        v
allow DDS discovery
        |
        v
count subscribers
        |
        v
publish message
        |
        v
process outgoing publication
        |
        v
destroy temporary publisher
```

---

## Dynamic Message Type Resolution

The publisher is not limited to a hard-coded ROS message class.

The requested message type is dynamically resolved.

For example:

```text
std_msgs/msg/String
```

is resolved to the corresponding generated ROS 2 message class.

The same architecture can therefore support message types such as:

```text
std_msgs/msg/String
std_msgs/msg/Bool
geometry_msgs/msg/Twist
sensor_msgs/msg/JointState
```

A particular message type must be installed and available in the active ROS 2 environment.

---

## Dynamic Message Population

The MCP request represents a ROS message as structured data.

Example:

```json
{
  "data": "hello"
}
```

The Jazzy adapter creates the actual ROS message object and populates its fields.

Conceptually:

```text
MCP dictionary
      |
      v
ROS message class
      |
      v
ROS message instance
      |
      v
set_message_fields
      |
      v
populated ROS message
```

This allows MCP clients to work with normal structured data while the ROS adapter handles generated ROS message objects.

---

## Topic Name Normalization

The requested topic name is normalized before publication.

For example:

```text
chatter
```

becomes:

```text
/chatter
```

An empty topic name is rejected.

---

## Message Type Validation

An empty message type is rejected.

An unknown or unavailable ROS message type also results in an error.

Example valid type:

```text
std_msgs/msg/String
```

Example invalid type:

```text
does_not_exist/msg/Fake
```

The adapter converts message type resolution failures into a controlled error.

---

## Message Validation

The MCP message must be represented as a dictionary.

For:

```text
std_msgs/msg/String
```

a valid message is:

```json
{
  "data": "hello"
}
```

The supplied fields must be compatible with the selected ROS message type.

Invalid or incompatible message fields result in an error.

---

## Temporary Publisher Lifecycle

The current implementation creates a publisher for one controlled publication.

```text
create publisher
      |
      v
publish one message
      |
      v
destroy publisher
```

The publisher is not permanently retained by the MCP server.

This keeps the initial implementation simple and avoids maintaining a dynamic publisher registry.

Persistent publishers may be introduced later if repeated or high-frequency publication becomes necessary.

---

## DDS Discovery

ROS 2 communication uses DDS discovery.

A publisher created immediately before publication may need a short opportunity to discover existing subscribers.

The implementation therefore provides a short discovery window before sending the message.

```text
create publisher
      |
      v
short discovery window
      |
      v
count subscribers
      |
      v
publish
```

This improves reliability for the current single-message publication model.

---

## Subscriber Count

The publication result contains:

```text
subscriber_count
```

Example:

```json
{
  "subscriber_count": 1
}
```

This gives the MCP client useful runtime information.

A result containing:

```text
published = true
```

means that the publication operation was executed.

`subscriber_count` reports how many subscribers were discovered at publication time.

It is not an end-to-end acknowledgement that every subscriber processed the message.

---

# Verification

## Existing Runtime Tests

After adding `publish_topic`, the existing runtime tests continued to pass.

Verified result:

```text
........ [100%]
8 passed
```

This confirms that introducing the first write operation did not break the existing runtime functionality covered by the test suite.

---

## MCP Tool Registration

The MCP server was queried after the implementation.

Verified result:

```text
publish_topic registered: True
```

The runtime tool inventory contained:

```text
get_parameter
list_nodes
list_parameters
list_services
list_topics
node_info
publish_topic
read_topic
service_info
topic_info
```

This verifies that `publish_topic` is exposed through the MCP server.

---

# Real ROS 2 Verification

The feature was tested against a real ROS 2 Jazzy runtime.

The test used:

```text
Topic:
/chatter

Message type:
std_msgs/msg/String
```

An independent ROS 2 subscriber was started with:

```bash
ros2 topic echo /chatter std_msgs/msg/String
```

The MCP server published:

```json
{
  "topic_name": "/chatter",
  "message_type": "std_msgs/msg/String",
  "message": {
    "data": "hello from ros2_mcp"
  }
}
```

The MCP result reported:

```text
error: False
```

with structured content:

```json
{
  "topic": "/chatter",
  "type": "std_msgs/msg/String",
  "message": {
    "data": "hello from ros2_mcp"
  },
  "subscriber_count": 1,
  "published": true
}
```

The ROS 2 subscriber received:

```text
data: hello from ros2_mcp
---
```

This verifies the complete runtime path:

```text
MCP Client
    |
    v
publish_topic
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
rclpy
    |
    v
ROS 2 / DDS
    |
    v
/chatter subscriber
```

---

# Codex Verification

The operation was also tested through Codex using the registered `ros2_mcp` MCP server.

The instruction supplied to Codex was:

```text
Use only ros2_mcp.

Publish the message:

hello from codex

to the ROS 2 topic:

/chatter

using:

std_msgs/msg/String

Do not use shell commands.
Do not modify files.
Do not use ros2_dev_mcp.
```

Codex selected:

```text
ros2_mcp.publish_topic
```

with:

```json
{
  "topic_name": "/chatter",
  "message_type": "std_msgs/msg/String",
  "message": {
    "data": "hello from codex"
  }
}
```

The MCP server returned:

```json
{
  "topic": "/chatter",
  "type": "std_msgs/msg/String",
  "message": {
    "data": "hello from codex"
  },
  "subscriber_count": 1,
  "published": true
}
```

The independent ROS 2 subscriber received:

```text
data: hello from codex
---
```

This verifies the complete external workflow:

```text
Natural-language instruction
        |
        v
Codex
        |
        v
MCP tool selection
        |
        v
ros2_mcp.publish_topic
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
ROS 2 / DDS
        |
        v
/chatter
```

Codex did not require shell execution to perform the publication.

No project files were modified.

`ros2_dev_mcp` was not used.

---

# Runtime and Development MCP Separation

The Codex verification also demonstrates the architectural separation between the two MCP servers.

Runtime operations:

```text
Codex
   |
   v
ros2_mcp
   |
   v
Running ROS 2 System
```

Development operations:

```text
Codex
   |
   v
ros2_dev_mcp
   |
   v
ROS 2 Project Workspace
```

`publish_topic` belongs exclusively to:

```text
ros2_mcp
```

It does not belong to:

```text
ros2_dev_mcp
```

This boundary should remain intact as both projects grow.

---

# Current Runtime Tool Set

After Phase 6 Step 1, `ros2_mcp` provides the following runtime capabilities.

## Read-Only Operations

```text
list_nodes
list_topics
topic_info
read_topic
node_info
list_parameters
get_parameter
list_services
service_info
```

## Controlled Write Operations

```text
publish_topic
```

The distinction between inspection and interaction is intentional.

---

# Safety Model

Introducing write operations changes the role of the runtime MCP server.

Earlier runtime operations primarily inspected ROS 2 state.

Phase 6 can actively affect a running ROS 2 graph.

Write operations must therefore remain explicit and narrowly scoped.

Preferred architecture:

```text
MCP Client
        |
        v
explicit MCP operation
        |
        v
validated arguments
        |
        v
RuntimeService
        |
        v
RosAdapter
        |
        v
controlled ROS operation
```

The runtime MCP should avoid exposing unrestricted shell execution such as:

```text
MCP Client
        |
        v
arbitrary shell command
        |
        v
ros2 ...
```

Explicit MCP operations provide an API surface that can be validated, tested, documented, and restricted.

---

## Physical Runtime Safety

A ROS 2 topic publication is not automatically harmless.

The meaning of a message depends on the target topic and receiving nodes.

For example:

```text
geometry_msgs/msg/Twist
```

published to a robot velocity command topic could cause physical robot motion.

Therefore:

```text
destructive_hint = false
```

does not mean that every possible publication is physically harmless.

It describes the generic MCP operation itself rather than the semantics of every possible target topic.

Robot-specific MCP servers and future physical control operations should introduce additional safety policies where appropriate.

---

# Current Limitations

The first `publish_topic` implementation intentionally has a limited scope.

Current limitations include:

- one publication per MCP call
- temporary publisher lifecycle
- no persistent publisher registry
- no streaming publication
- no configurable publication rate
- no configurable QoS through the MCP interface
- no topic allowlist yet
- no message-type allowlist yet
- no robot-specific safety policy yet
- no acknowledgement that a subscriber processed the message
- no ROS 2 Action support yet

These limitations keep the first controlled write capability small and understandable.

They can be addressed incrementally when required.

---

# Why `publish_topic` Is Important

`publish_topic` changes `ros2_mcp` from a purely observational interface into a controlled ROS 2 interaction layer.

Before this step, an MCP client could inspect:

```text
nodes
topics
services
parameters
topic messages
```

After this step, an MCP client can initiate a ROS 2 runtime operation.

This enables workflows such as:

```text
inspect ROS graph
        |
        v
understand available interfaces
        |
        v
select an explicit MCP operation
        |
        v
interact with ROS 2
        |
        v
inspect the result
```

This generic runtime capability provides an important foundation for later ROS 2 integrations.

---

# Future Specialized MCP Servers

Generic runtime capabilities should remain in `ros2_mcp`.

Specialized ROS 2 subsystems can later be implemented as separate MCP servers.

Examples:

```text
ros2_control_mcp
nav2_mcp
moveit2_mcp
```

Conceptually:

```text
                    MCP Client
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
    ros2_mcp       ros2_dev_mcp    Specialized MCPs
        |               |                |
        v               v                +--> ros2_control
 ROS 2 runtime     ROS 2 projects        +--> Nav2
                                         +--> MoveIt 2
```

This prevents the generic runtime MCP from becoming a monolithic server containing every ROS 2 subsystem.

---

# Files Modified for Step 1

Phase 6 Step 1 modifies:

```text
src/ros2_mcp/ros/adapter.py
src/ros2_mcp/ros/jazzy/adapter.py
src/ros2_mcp/application/runtime/service.py
src/ros2_mcp/mcp/runtime_tools.py
tests/unit/test_runtime_service.py
```

Phase 6 documentation is maintained in:

```text
docs/README_PHASE_6_RUNTIME_INTERACTION.md
```

---

# Phase 6 Progress

Current status:

```text
Phase 6 – Controlled ROS 2 Runtime Interaction

[COMPLETE] Step 1 – publish_topic
[PLANNED]  Step 2 – call_service
[PLANNED]  Step 3 – set_parameter
```

The scope is intentionally expanded one controlled operation at a time.

---

# Next Step

The next planned capability is:

```text
call_service
```

The intended architecture is:

```text
MCP Client
    |
    v
call_service
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
Dynamic ROS Service Client
    |
    v
ROS 2 Service Server
```

The implementation should dynamically resolve the ROS service type, construct the request from structured MCP input, call the service, and return the response as structured data.

Example future operation:

```text
call_service(
    service_name="/example_service",
    service_type="std_srvs/srv/SetBool",
    request={
        "data": true
    }
)
```

The service implementation should follow the same principles established by `publish_topic`:

- explicit MCP operation
- structured arguments
- no arbitrary shell execution
- RuntimeService delegation
- RosAdapter abstraction
- Jazzy-specific implementation behind the adapter
- controlled error handling
- real ROS 2 verification
- Codex verification

---

# Phase 6 Status

Phase 6 is currently in progress.

The first controlled ROS 2 write operation has been implemented and successfully verified:

```text
publish_topic
```

Verification has been completed at three levels:

```text
Existing Runtime Tests
        |
        v
Direct MCP Client Test
        |
        v
Codex -> ros2_mcp -> ROS 2
```

The real ROS 2 Jazzy runtime received both test publications successfully.

The next implementation step is:

```text
call_service
```

After `call_service`, the planned next controlled runtime operation is:

```text
set_parameter
```
