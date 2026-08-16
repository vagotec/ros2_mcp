# ros2_mcp

A standards-based Model Context Protocol (MCP) server for ROS 2.

`ros2_mcp` provides AI agents and MCP-compatible clients with structured access to a ROS 2 runtime without exposing an arbitrary shell or unrestricted ROS CLI interface.

The project currently targets:

- ROS 2 Jazzy
- Ubuntu 24.04 LTS
- Python 3.12
- MCP Python SDK 2.0.0
- MCP Protocol `2026-07-28`

The server supports both local MCP communication through `stdio` and remote communication through MCP Streamable HTTP.

---

## Project Status

Current development status:

```text
Version:              v0.1.0 release candidate
ROS distribution:     ROS 2 Jazzy
MCP SDK:              2.0.0
MCP protocol:         2026-07-28

MCP tools:            46
Prompts:              6
Resource templates:   9

Transports:
  stdio               PASS
  Streamable HTTP     PASS

Remote authentication:
  Bearer token        PASS

Test suite:
  48 passed
```

Development phases:

```text
Phase 1    Runtime foundation                         COMPLETE
Phase 2    ROS graph discovery                        COMPLETE
Phase 3    Topic runtime inspection                   COMPLETE
Phase 4    Runtime architecture expansion             COMPLETE
Phase 5    Extended runtime inspection                COMPLETE
Phase 6    Controlled runtime interaction             COMPLETE
Phase 7    Advanced runtime operations                COMPLETE
Phase 8    Packaging and deployment readiness         COMPLETE
Phase 9    MCP protocol modernization                 COMPLETE
Phase 10   MCP resources                              COMPLETE
Phase 11   MCP prompts                                COMPLETE
Phase 12   MCP resource templates                     COMPLETE
Phase 13   MCP client compatibility                   COMPLETE
Phase 14   Remote MCP / Streamable HTTP               COMPLETE
```

The generic ROS 2 MCP runtime foundation is considered feature-complete for the `v0.1.0` scope.

---

# Why ros2_mcp?

ROS 2 already provides powerful command-line and programmatic APIs.

AI agents, however, should not require unrestricted shell access to interact with a robot runtime.

`ros2_mcp` provides a controlled layer between MCP clients and ROS 2.

```text
AI Agent / MCP Client
        |
        v
       MCP
        |
        v
     ros2_mcp
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
    ROS 2 Jazzy
```

The MCP layer does not directly depend on `rclpy`.

ROS-specific functionality is isolated behind adapters so that MCP transport, application logic, and ROS runtime implementation remain separate.

---

# Design Goals

The project follows several architectural principles:

- keep MCP and ROS 2 concerns separated
- isolate `rclpy` behind a ROS adapter
- keep ROS distributions replaceable
- keep MCP clients replaceable
- avoid arbitrary shell execution
- avoid arbitrary ROS CLI execution
- distinguish read and write operations
- make runtime writes explicit
- expose safety policies to MCP clients
- manage runtime resources instead of spawning uncontrolled processes
- keep runtime resource usage bounded
- prefer official ROS 2 APIs
- prefer stable MCP SDK APIs
- remain independent of client-specific implementations
- keep subsystem-specific robotics semantics outside the generic runtime server

---

# Architecture

The high-level architecture is:

```text
                        MCP Client
                            |
               +------------+------------+
               |                         |
               v                         v
            stdio                 Streamable HTTP
               |                         |
               +------------+------------+
                            |
                            v
                        MCPServer
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
        Tools           Resources          Prompts
          |                 |                 |
          +-----------------+-----------------+
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
                     ROS 2 Jazzy
```

Transport concerns remain outside the ROS runtime implementation.

The same runtime functionality is therefore available to local and remote MCP clients.

---

# MCP Capabilities

`ros2_mcp` exposes ROS 2 through several MCP capability types.

```text
MCP
 |
 +-- Tools
 |
 +-- Resources
 |
 +-- Resource Templates
 |
 +-- Prompts
 |
 +-- stdio transport
 |
 +-- Streamable HTTP transport
```

Tools provide executable runtime operations.

Resources provide structured read access.

Resource templates provide parameterized resource access.

Prompts provide reusable workflows for MCP clients.

---

# ROS Graph Discovery

The server can inspect the active ROS graph.

Supported functionality includes:

- node discovery
- node inspection
- topic discovery
- service discovery
- action discovery
- interface discovery

This allows an MCP client to discover the ROS runtime dynamically instead of relying on a hard-coded robot configuration.

---

# Topics

Topic functionality includes:

```text
topic discovery
topic information
single-message reading
multi-message reading
topic publishing
QoS inspection
QoS recommendation
automatic QoS selection
persistent publishers
```

The runtime can dynamically resolve ROS message interfaces and work with discovered topic types.

Automatic QoS handling helps clients subscribe to existing publishers without requiring detailed DDS knowledge.

---

# Services

Service functionality includes:

```text
service discovery
service inspection
service calls
dynamic service type resolution
```

Requests are represented as structured MCP arguments and converted into the corresponding ROS service request types.

---

# Parameters

Parameter functionality includes:

```text
parameter discovery
parameter reading
parameter writing
```

Parameter writes pass through the runtime safety layer.

---

# ROS 2 Actions

ROS 2 Action support includes:

```text
action discovery
action inspection
action goal execution
action feedback
action results
managed action sessions
action status
action cancellation
```

Action operations are managed by the runtime rather than exposed as uncontrolled ROS CLI commands.

---

# ROS Interfaces

The server can discover and inspect ROS interface definitions.

Supported interface categories include:

```text
messages
services
actions
```

This allows MCP clients to understand ROS types before performing runtime operations.

---

# QoS

ROS 2 QoS support includes:

```text
QoS inspection
QoS recommendation
automatic QoS selection
```

The runtime can derive compatible subscription settings from existing publishers.

This is particularly important when interacting with sensor topics that use profiles such as `BEST_EFFORT`.

---

# Diagnostics and Runtime Health

Runtime observability includes:

```text
ROS logging
diagnostic information
runtime health
```

MCP clients can inspect runtime state without requiring direct shell access.

---

# Lifecycle Nodes

ROS 2 Lifecycle operations are supported through managed runtime functionality.

This provides a generic foundation for future ROS 2 subsystems that rely on lifecycle-managed nodes.

---

# Managed ROS Processes

`ros2_mcp` can start and manage approved ROS processes.

Process management is intentionally restricted.

The server does not expose an arbitrary shell.

```text
MCP Client
    |
    v
start_ros_process
    |
    v
Safety validation
    |
    v
ROS package resolution
    |
    v
Managed process
```

Only processes created and tracked by the MCP runtime can be stopped through managed stop operations.

---

# Managed ROS Launch

ROS launch files can be started through managed launch operations.

Launch files must resolve through the ROS package infrastructure.

The runtime does not accept arbitrary filesystem paths as unrestricted launch targets.

Managed launch functionality includes:

```text
launch start
launch status
launch stop
resource tracking
package resolution
```

---

# rosbag

Managed rosbag functionality includes:

```text
recording
playback
bag information
managed stop operations
```

Bag resources are tracked by the runtime and subject to configured resource limits.

---

# Safety Model

Runtime safety is a central part of the architecture.

The server intentionally avoids unrestricted execution interfaces.

Important safety properties include:

```text
arbitrary shell execution          disabled
arbitrary ROS CLI execution        disabled

managed process stop only          enabled
managed launch stop only           enabled
managed rosbag stop only           enabled

package resolution required        enabled
launch resolution required         enabled

path traversal protection          enabled
structured argument validation     enabled
protected ROS resources            enabled
runtime resource limits            enabled
dry-run validation                 enabled
```

---

# Protected ROS Resources

Sensitive ROS resources can be protected through configuration.

Examples include:

```text
/parameter_events
/rosout
```

Configuration supports policies for:

```text
protected_topics
protected_services
protected_parameters
protected_actions

allowed_process_packages
allowed_launch_packages
```

Deployments can therefore tighten runtime permissions without modifying application code.

---

# Runtime Resource Limits

Managed runtime objects are bounded.

The default configuration includes limits for resources such as:

```text
persistent publishers
managed processes
managed launches
bag recordings
bag playbacks
```

This prevents an MCP client from creating unlimited runtime resources.

---

# Dry-Run Validation

Potentially disruptive managed operations support dry-run validation.

Examples include:

```text
start_ros_process
start_ros_launch
start_bag_recording
start_bag_playback
```

A client can therefore validate an operation before requesting its execution.

---

# MCP Resources

In addition to executable MCP Tools, `ros2_mcp` exposes ROS runtime information through MCP Resources.

Resources are intended for structured read-only access.

Conceptually:

```text
MCP Client
    |
    v
resources/read
    |
    v
ros2://...
    |
    v
ROS Runtime
```

Resources complement tools instead of replacing them.

Tools remain appropriate for operations and state changes.

Resources are appropriate for runtime information that can naturally be represented as readable MCP data.

---

# MCP Resource Templates

Parameterized ROS runtime information is exposed through MCP Resource Templates.

The current implementation provides:

```text
9 resource templates
```

Templates allow MCP clients to discover resource URI patterns and instantiate them with runtime-specific values.

This avoids creating a permanently registered MCP resource for every possible ROS entity.

---

# MCP Prompts

Reusable ROS-oriented workflows are available through MCP Prompts.

The current implementation provides:

```text
6 prompts
```

Prompts allow MCP clients to discover common ROS workflows without embedding client-specific instructions into the runtime implementation.

An example workflow is a ROS runtime health check.

Prompts remain independent of a specific LLM or MCP client.

---

# MCP Protocol

The current protocol baseline is:

```text
2026-07-28
```

Protocol negotiation is handled by the MCP SDK.

The project avoids implementing private client-specific protocol behavior.

Compatibility has been verified through real MCP client interactions.

---

# Local MCP Transport

The default local transport is MCP over `stdio`.

```text
MCP Client
    |
    v
stdio
    |
    v
ros2-mcp
    |
    v
ROS 2
```

This transport is appropriate when the MCP client and ROS runtime execute on the same machine.

---

# Streamable HTTP

Remote MCP access is available through MCP Streamable HTTP.

```text
Remote MCP Client
        |
        v
       HTTP
        |
        v
Streamable HTTP
        |
        v
    ros2_mcp
        |
        v
      ROS 2
```

The HTTP server uses a dedicated entry point:

```text
ros2-mcp-http
```

Remote access does not duplicate ROS runtime functionality.

Both transports use the same MCP server and runtime services.

---

# HTTP Security

Remote exposure is explicit.

The Streamable HTTP implementation includes:

```text
DNS rebinding protection
Host validation
Origin validation
optional Bearer authentication
OAuth Protected Resource Metadata
```

The default configuration is intended to avoid accidentally exposing the ROS runtime to arbitrary network clients.

Network deployments should always review the HTTP and authentication configuration before exposing the service outside a trusted environment.

---

# Bearer Authentication

Streamable HTTP can require Bearer authentication.

When authentication is enabled:

```text
MCP Client
    |
    | Authorization: Bearer <token>
    v
HTTP authentication
    |
    v
MCP server
    |
    v
ROS runtime
```

Requests without valid credentials are rejected.

Authentication has been validated with real MCP client operations, including ROS runtime tool calls.

---

# OAuth Protected Resource Metadata

When HTTP authentication is enabled, the server exposes OAuth Protected Resource Metadata for the MCP endpoint.

The MCP resource metadata route follows the MCP endpoint path.

Example:

```text
/.well-known/oauth-protected-resource/mcp
```

Metadata describes information such as:

```text
resource
authorization_servers
scopes_supported
bearer_methods_supported
```

This allows standards-aware MCP clients to discover the authentication requirements of the protected MCP resource.

---

# Configuration

Runtime configuration is centralized.

The packaged default configuration is:

```text
src/ros2_mcp/config/default.toml
```

Configuration resolution follows:

```text
explicit configuration path
        |
        v
ROS2_MCP_CONFIG
        |
        v
packaged default.toml
```

An explicitly selected configuration file must exist.

Invalid explicit configuration does not silently fall back to the packaged default.

---

# Installation

Clone the repository and create the project environment.

```bash
cd ~/projects/robotics/ros2_mcp
source /opt/ros/jazzy/setup.bash

uv sync
source .venv/bin/activate
```

The project uses `uv` for Python environment and dependency management.

---

# Local Development Run

Activate the environment and ROS 2:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2-mcp
```

The process communicates with the MCP client through `stdio`.

---

# Streamable HTTP Run

Start the remote MCP server with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2-mcp-http
```

HTTP host, port, MCP path, security settings, and authentication behavior are controlled through the project configuration.

---

# External Configuration

An external configuration can be selected with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS2_MCP_CONFIG="$PWD/config/ros2_mcp.toml"

ros2-mcp
```

The same configuration architecture is used by the HTTP transport.

---

# MCP Client Compatibility

The implementation is designed to remain independent of individual MCP clients.

The server has been validated using MCP SDK clients and Codex integration.

The architecture is intentionally:

```text
client independent
transport independent
ROS adapter based
```

A client should interact with standard MCP capabilities rather than private `ros2_mcp` protocol extensions.

---

# Codex Integration

`ros2_mcp` can be used as an MCP server by Codex.

Conceptually:

```text
Codex
  |
  v
 MCP
  |
  v
ros2_mcp
  |
  v
ROS 2 Jazzy
```

Both source-tree and installed-package integration have been validated during project development.

The MCP server itself does not contain Codex-specific ROS runtime logic.

---

# Packaging

The project can be built as a Python wheel and source distribution.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf dist
uv build
```

Expected artifacts include:

```text
*.whl
*.tar.gz
```

The packaged default configuration is included in the Python package.

---

# Installed Package

The project has been tested outside the source repository through an isolated wheel installation.

The validated deployment path is:

```text
source repository
      |
      v
   uv build
      |
      v
     wheel
      |
      v
isolated environment
      |
      v
installed ros2-mcp
      |
      +----------------+
      |                |
      v                v
    stdio        Streamable HTTP
      |                |
      +-------+--------+
              |
              v
           ROS 2
```

This verifies that runtime operation does not depend on the repository working directory.

---

# Testing

Run the complete automated test suite with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
pytest --collect-only -q
git diff --check
```

Current validated result:

```text
48 passed
```

The test suite covers unit, integration, regression, MCP transport, authentication, and HTTP behavior.

---

# Real ROS 2 Verification

The implementation has also been tested against a real ROS 2 Jazzy runtime.

Verified areas include:

```text
ROS graph discovery

topic discovery
topic inspection
topic reading
multi-message topic reading
topic publishing

service calls

parameter writes

action discovery
action inspection
action execution
action feedback
action results
action cancellation

interface discovery

ROS logging
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

runtime safety rejection

executor concurrency

MCP stdio access
MCP Streamable HTTP access
authenticated MCP HTTP access
```

Real runtime testing is important because DDS, QoS, executors, ROS graph behavior, and lifecycle interactions cannot be fully validated through isolated unit tests.

---

# Important Runtime Issues Already Addressed

Development and real ROS testing exposed several runtime issues that were subsequently corrected.

These included:

```text
diagnostic severity normalization
BEST_EFFORT / RELIABLE QoS compatibility
executor concurrent spinning
ROS package resolution for launch
MCP client protocol compatibility
Streamable HTTP lifecycle behavior
authenticated remote MCP access
```

These cases are covered by the current architecture and regression testing where appropriate.

---

# Repository Structure

A simplified project structure is:

```text
ros2_mcp/
├── docs/
├── src/
│   └── ros2_mcp/
│       ├── application/
│       ├── config/
│       ├── mcp/
│       ├── project/
│       ├── ros/
│       │   └── jazzy/
│       ├── http_server.py
│       └── server.py
├── tests/
│   ├── integration/
│   └── unit/
├── pyproject.toml
├── uv.lock
└── README.md
```

The exact internal structure may evolve while preserving the architectural separation between MCP, application services, configuration, and ROS adapters.

---

# Development Documentation

Detailed development history is kept separately from this README.

```text
docs/
├── README_PHASE_1.md
├── README_PHASE_2.md
├── README_PHASE_3.md
├── README_PHASE_4.md
├── README_PHASE_5.md
├── README_PHASE_6.md
├── README_PHASE_7.md
├── README_PHASE_8.md
├── README_PHASE_9.md
├── README_PHASE_10.md
├── README_PHASE_11.md
├── README_PHASE_12.md
├── README_PHASE_13.md
└── README_PHASE_14.md
```

The root README describes the current project.

The phase documents describe how the architecture was developed and validated.

---

# Scope

`ros2_mcp` is intentionally a generic ROS 2 runtime MCP server.

Its responsibility is to expose generic ROS 2 concepts such as:

```text
nodes
topics
services
parameters
actions
interfaces
QoS
lifecycle
diagnostics
ROS processes
ROS launch
rosbag
runtime health
```

Subsystem-specific robotics semantics are intentionally not embedded into the generic server.

---

# Intentional Boundaries

The following capabilities are intentionally outside the `ros2_mcp` `v0.1.0` scope:

```text
ROS 1 compatibility

arbitrary shell execution
arbitrary ROS CLI execution

robot-specific application logic

camera image processing
camera-specific perception

LiDAR-specific perception

ros2_control-specific semantics
Nav2-specific semantics
MoveIt 2-specific semantics

robot-specific physical safety
controller-specific safety
navigation-specific safety
manipulation-specific safety
```

These are architectural boundaries rather than missing generic ROS runtime features.

---

# ROS 1

ROS 1 is not supported.

The project is designed specifically around ROS 2 concepts including:

```text
DDS
rclpy
ROS 2 Actions
ROS 2 Lifecycle
ROS 2 QoS
ROS 2 interfaces
```

ROS 1 would require a different runtime and communication model and is outside the project scope.

---

# ros2_control, Nav2 and MoveIt 2

Subsystem-specific functionality is intentionally not implemented directly in this repository.

That includes specialized semantics for:

```text
ros2_control
Nav2
MoveIt 2
```

The generic functionality required by these systems remains available through normal ROS 2 primitives.

For example:

```text
ros2_control
    |
    +-- topics
    +-- services
    +-- parameters
    +-- lifecycle
    +-- interfaces

Nav2
    |
    +-- actions
    +-- topics
    +-- services
    +-- parameters
    +-- lifecycle

MoveIt 2
    |
    +-- actions
    +-- topics
    +-- services
    +-- parameters
```

Application-specific interpretation of these interfaces belongs outside the generic `ros2_mcp` runtime.

---

# Camera and Perception Boundary

Camera-specific image retrieval and perception are intentionally not implemented as generic MCP runtime operations.

ROS camera topics can still be discovered and inspected through the normal ROS graph functionality.

Specialized perception systems may independently build on:

```text
sensor_msgs/Image
sensor_msgs/CameraInfo
sensor_msgs/PointCloud2
image_transport
depth streams
camera-specific APIs
```

Keeping perception outside the generic runtime prevents `ros2_mcp` from becoming a monolithic robotics framework.

---

# Future Architecture

The generic runtime can serve as a foundation for higher-level robotics integrations.

Conceptually:

```text
                 AI Agent
                    |
                    v
                   MCP
                    |
        +-----------+-----------+
        |                       |
        v                       v
    ros2_mcp              Higher-level
 Generic Runtime          Robotics MCP
        |                       |
        +-----------+-----------+
                    |
                    v
                  ROS 2
                    |
                    v
             Robot Hardware
```

The generic server remains responsible for ROS 2 runtime primitives.

Higher-level systems can add robot, controller, navigation, manipulation, or perception semantics without changing the generic runtime architecture.

---

# Hardware Independence

`ros2_mcp` does not depend on a specific robot platform.

It can operate against ROS 2 systems containing components such as:

```text
mobile robots
robot arms
cameras
LiDAR sensors
IMUs
motor controllers
servo controllers
simulation systems
```

Hardware-specific behavior remains in ROS drivers and higher-level robotics software.

---

# Distribution Architecture

The current ROS implementation lives behind a Jazzy-specific adapter.

Conceptually:

```text
MCP
 |
 v
RuntimeService
 |
 v
RosAdapter
 |
 +--> JazzyRosAdapter
 |
 +--> future ROS distribution adapter
```

This architecture reduces coupling between MCP functionality and a particular ROS distribution.

The current supported target remains ROS 2 Jazzy.

---

# Security Considerations

`ros2_mcp` can control a live ROS runtime.

Deployments should therefore treat MCP access as privileged robot access.

Important recommendations include:

- do not expose the MCP HTTP endpoint directly to an untrusted network
- enable authentication for remote deployments
- restrict allowed hosts and origins
- use network-level access controls
- use TLS termination when crossing untrusted networks
- configure protected ROS resources
- restrict process and launch package allowlists
- review runtime resource limits
- keep physical robot safety outside the LLM/MCP layer
- use ROS and hardware safety mechanisms for real actuators

Bearer authentication protects access to the MCP endpoint but is not a replacement for transport encryption.

---

# What ros2_mcp Is Not

`ros2_mcp` is not:

```text
a replacement for ROS 2

a replacement for DDS

a robot controller

a motion planner

a navigation stack

a perception framework

a ros2_control replacement

a MoveIt 2 replacement

a Nav2 replacement

an unrestricted remote shell
```

It is a controlled MCP interface to a ROS 2 runtime.

---

# Project Philosophy

The project is developed independently.

Other ROS MCP implementations may be evaluated for:

```text
feature comparison
architecture comparison
protocol compatibility
missing capability analysis
```

Their source code is not used as a copy-and-paste implementation basis.

The goal is to maintain a small, understandable, standards-oriented ROS 2 MCP architecture.

---

# Release v0.1.0

The `v0.1.0` release scope consists of:

```text
generic ROS 2 runtime access
46 MCP runtime tools
MCP resources
MCP resource templates
MCP prompts
MCP protocol 2026-07-28
stdio transport
Streamable HTTP transport
optional Bearer authentication
OAuth Protected Resource Metadata
HTTP security controls
runtime safety guardrails
ROS 2 Jazzy adapter
packaged configuration
wheel / sdist packaging
real ROS 2 validation
MCP client compatibility validation
48 automated tests
```

Before promoting the development branch to `main`, the repository should pass:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
pytest --collect-only -q
git diff --check
git status
```

Expected automated test result:

```text
48 passed
```

After the release verification, the validated `dev` branch can be promoted to `main` and tagged as `v0.1.0`.

---

# Current Status

```text
ROS 2 Jazzy runtime foundation       COMPLETE

46 MCP tools                         COMPLETE

MCP Resources                        COMPLETE
MCP Resource Templates               COMPLETE
MCP Prompts                          COMPLETE

MCP 2026-07-28                       COMPLETE

stdio transport                      COMPLETE
Streamable HTTP                      COMPLETE

Bearer authentication                COMPLETE
Protected Resource Metadata          COMPLETE
HTTP security controls               COMPLETE

Runtime safety                       COMPLETE
Runtime resource management          COMPLETE

Wheel / sdist packaging              COMPLETE
Installed-package verification       COMPLETE

Real ROS 2 verification              COMPLETE
MCP client compatibility             COMPLETE

Automated tests                      48 PASSED

v0.1.0                               RELEASE CANDIDATE
```

`ros2_mcp` is ready for final release verification and promotion from `dev` to `main`.

---

# License

Licensed under the Apache License 2.0.

Copyright 2026 Vagotec.
