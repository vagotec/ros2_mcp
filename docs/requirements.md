# ros2_mcp Requirements

This document defines the requirements for:

1. Developing and extending `ros2_mcp`
2. Starting and using the `ros2_mcp` MCP server
3. Maintaining the project architecture
4. Maintaining runtime safety
5. Local MCP operation through stdio
6. Remote MCP operation through Streamable HTTP
7. Authentication and HTTP transport security
8. Packaging, testing, and release validation

The Python package dependencies themselves are managed through:

```text
pyproject.toml
uv.lock
```

---

# 1. Requirements for Developing ros2_mcp

## 1.1 Supported Environment

The current development environment is based on:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.12
- `uv`
- MCP Python SDK 2.x
- `rclpy`
- pytest
- Git

The currently validated MCP Python SDK version is:

```text
2.0.0
```

The current implementation targets ROS 2 Jazzy.

ROS-specific functionality must remain isolated behind the ROS adapter architecture so that future ROS 2 distributions can be supported without redesigning the MCP and application layers.

ROS 1 is intentionally not supported.

---

## 1.2 Project Location

The development repository is expected at:

```text
~/projects/robotics/ros2_mcp
```

Before development, testing, or running project-local commands:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

---

## 1.3 Required System Software

The development system requires:

```text
Ubuntu 24.04 LTS
ROS 2 Jazzy
Python 3.12
Git
uv
```

Verify the environment with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python --version
uv --version
git --version
echo "$ROS_DISTRO"
```

Expected ROS distribution:

```text
jazzy
```

---

## 1.4 Python Environment

The project uses a local virtual environment:

```text
.venv/
```

Create or synchronize the environment with:

```bash
cd ~/projects/robotics/ros2_mcp

uv sync

source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Python dependencies are defined in:

```text
pyproject.toml
```

The reproducible dependency state is recorded in:

```text
uv.lock
```

Do not manually maintain a duplicate Python `requirements.txt` dependency list unless a future distribution requirement explicitly requires one.

---

## 1.5 ROS 2 Python Environment

`ros2_mcp` uses the ROS 2 Jazzy Python client library `rclpy`.

After activating the project environment, the ROS 2 environment must also be sourced:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -c "import rclpy; print(rclpy.__file__)"
```

A normal Jazzy installation should resolve `rclpy` from:

```text
/opt/ros/jazzy/
```

The project must not vendor or duplicate `rclpy`.

---

## 1.6 Development Architecture

New functionality must preserve the existing architecture:

```text
MCP Client
    |
    v
Transport
    |
    v
MCP Layer
    |
    v
Application / RuntimeService
    |
    v
ROS Adapter Interface
    |
    v
JazzyRosAdapter
    |
    v
rclpy / ROS 2 Jazzy
```

The following separation must be preserved:

```text
MCP protocol
    !=
transport
    !=
application logic
    !=
ROS implementation
```

MCP tools must not directly contain ROS 2 implementation logic.

ROS 2 Jazzy-specific functionality belongs under:

```text
src/ros2_mcp/ros/jazzy/
```

The generic ROS adapter contract belongs under:

```text
src/ros2_mcp/ros/
```

Application orchestration belongs under:

```text
src/ros2_mcp/application/
```

MCP-facing functionality belongs under:

```text
src/ros2_mcp/mcp/
```

---

## 1.7 Transport Independence

The runtime architecture must remain independent from the MCP transport.

Supported transports are:

```text
stdio
Streamable HTTP
```

Both transports must expose the same MCP runtime server.

The architecture is:

```text
                    +--- stdio
                    |
MCP Client ---------+
                    |
                    +--- Streamable HTTP
                              |
                              v
                          MCPServer
                              |
                              v
                        RuntimeService
                              |
                              v
                         RosAdapter
                              |
                              v
                        ROS 2 Jazzy
```

ROS runtime functionality must not be duplicated between transports.

---

## 1.8 MCP Protocol Requirements

The current protocol baseline is:

```text
2026-07-28
```

The project must use supported MCP SDK functionality rather than manually reimplementing MCP protocol behavior.

Client-specific workarounds should be avoided.

The server should remain compatible with standards-based MCP clients.

---

## 1.9 MCP Capability Baseline

The current validated MCP capability inventory is:

```text
46 MCP tools
6 MCP prompts
0 static MCP resources
9 MCP resource templates
```

A change must not unintentionally reduce these baselines.

Intentional capability changes require corresponding:

```text
implementation changes
tests
documentation
release notes where appropriate
```

---

## 1.10 Configuration Requirements

Runtime configuration must not be hard-coded into the implementation.

The packaged default configuration is:

```text
src/ros2_mcp/config/default.toml
```

Configuration loading is implemented through:

```text
src/ros2_mcp/config/settings.py
```

An external configuration can be selected through:

```text
ROS2_MCP_CONFIG
```

Example:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS2_MCP_CONFIG="$HOME/my_ros2_mcp.toml"

ros2-mcp
```

Configuration resolution must follow:

```text
explicit configuration
        |
        v
ROS2_MCP_CONFIG
        |
        v
packaged default configuration
```

An explicitly configured invalid or missing file must not silently fall back to the packaged default.

---

## 1.11 Backward-Compatible Configuration

Configuration files created before Streamable HTTP support may not contain an `[http]` section.

The configuration loader must provide safe HTTP defaults for such legacy configurations.

Existing stdio configurations must continue to work without requiring HTTP configuration.

---

## 1.12 Safety Requirements

New write-capable ROS operations must integrate with the existing safety model.

The safety layer is implemented under:

```text
src/ros2_mcp/ros/jazzy/safety.py
```

Important principles include:

- no arbitrary shell execution
- no arbitrary ROS CLI execution
- structured subprocess arguments
- package resolution before process execution
- launch-file resolution before launch execution
- managed resources may only be stopped by their owning manager
- protected ROS topics
- protected ROS services
- protected ROS parameters
- protected ROS actions
- resource limits
- timeout protection
- dry-run support for potentially destructive or process-starting operations

New runtime operations must not bypass these checks.

---

## 1.13 Subprocess Requirements

Where external ROS commands are required, structured subprocess execution must be used.

Do not introduce:

```python
shell=True
```

Arguments must be passed as structured argument lists.

Example:

```python
subprocess.Popen(
    [
        "ros2",
        "run",
        package_name,
        executable,
    ]
)
```

Do not construct arbitrary shell command strings from MCP input.

---

## 1.14 ROS CLI Boundary

`ros2_mcp` must not expose an unrestricted MCP operation equivalent to:

```text
ros2 <arbitrary user supplied arguments>
```

ROS CLI subprocesses may only be used internally when their structure and arguments are controlled and validated by the implementation.

---

## 1.15 ROS Executor Requirements

ROS executor access must remain serialized through the shared adapter executor helpers.

ROS modules must not independently perform uncontrolled concurrent executor spins.

This protects the shared `rclpy` executor from concurrent MCP requests.

Any new functionality requiring executor spinning must use the existing executor synchronization mechanism in `JazzyRosAdapter`.

---

## 1.16 QoS Requirements

Topic operations must support ROS 2 QoS correctly.

For general topic reads, automatic QoS selection should remain the preferred default where applicable.

The current QoS implementation is located in:

```text
src/ros2_mcp/ros/jazzy/qos.py
src/ros2_mcp/ros/jazzy/qos_auto.py
```

New topic functionality should reuse these components rather than implementing independent QoS logic.

---

## 1.17 Managed Resource Requirements

Runtime resources created by `ros2_mcp` must be tracked by their owning manager.

Examples include:

```text
persistent publishers
managed processes
managed launches
bag recordings
bag playbacks
Action goals
```

A manager must not stop or modify resources that it does not own.

---

## 1.18 Resource Limits

Managed runtime resources must remain bounded.

Resource limits should exist for managed resource types where uncontrolled creation could affect runtime stability.

New managed resource types must define:

```text
ownership
lifecycle
cleanup
limits
timeout behavior where applicable
```

---

## 1.19 Protected ROS Resources

The safety configuration supports protected:

```text
topics
services
parameters
actions
```

Write-capable operations must check the corresponding protection policy before modifying ROS runtime state.

---

## 1.20 Process Safety

Managed process execution must resolve through ROS package infrastructure.

Arbitrary executable filesystem paths must not replace ROS package resolution.

Where package allowlists are configured, they must be enforced.

---

## 1.21 Launch Safety

Managed launch execution must resolve launch files through installed ROS packages and the ament index.

Arbitrary user-provided launch filesystem paths must not bypass package resolution.

Where launch package allowlists are configured, they must be enforced.

---

## 1.22 Structured Argument Validation

Subprocess arguments must be validated.

Unsafe values such as the following must be rejected where applicable:

```text
NUL characters
unexpected newlines
carriage returns
excessive argument lengths
excessive argument counts
```

Structured subprocess arguments must never be converted into unrestricted shell commands.

---

## 1.23 Path Traversal Protection

Managed resource names and filesystem-related inputs must reject path traversal attempts such as:

```text
../bad
```

Future filesystem-facing functionality must preserve this requirement.

---

## 1.24 ROS Action Requirements

ROS 2 Actions support synchronous and managed execution.

Managed Action operations include:

```text
start_action_goal
get_action_status
cancel_action_goal
```

Managed Action state includes:

```text
goal
status
completed
result
feedback
```

Action feedback is available through the managed Action status model.

A separate feedback-specific MCP tool is not required for the current release.

---

## 1.25 Lifecycle Requirements

Generic ROS 2 lifecycle functionality belongs in `ros2_mcp`.

Lifecycle operations must use controlled ROS 2 lifecycle APIs.

Subsystem-specific lifecycle semantics should remain outside the generic runtime layer.

---

## 1.26 rosbag Requirements

Managed rosbag functionality must preserve:

```text
managed recording lifecycle
managed playback lifecycle
validated bag names
resource ownership
resource limits
safe cleanup
dry-run support where applicable
```

The server must not expose unrestricted arbitrary rosbag shell commands.

---

## 1.27 Runtime Health Requirements

Runtime health should aggregate generic ROS 2 information such as:

```text
graph
diagnostics
rosout
```

Subsystem-specific health interpretation belongs outside the generic runtime layer.

---

# 2. Requirements for Streamable HTTP

## 2.1 HTTP Server

The Streamable HTTP server entry point is:

```text
ros2-mcp-http
```

It must use the same MCP server architecture as the stdio transport.

The HTTP implementation must not duplicate ROS runtime functionality.

---

## 2.2 HTTP Configuration

The HTTP configuration must support:

```text
host
port
path
enable_dns_rebinding_protection
allowed_hosts
allowed_origins
```

Safe packaged defaults must bind to:

```text
127.0.0.1
```

Remote network exposure must require explicit configuration.

---

## 2.3 DNS Rebinding Protection

DNS rebinding protection must remain enabled by default.

The implementation must validate:

```text
Host
Origin
```

according to the configured transport security policy.

Validated behavior:

```text
invalid Origin
    -> HTTP 403

invalid Host
    -> HTTP 421
```

---

## 2.4 Authentication Architecture

HTTP authentication must remain separate from ROS runtime logic.

The architecture is:

```text
Remote MCP Client
       |
       v
Streamable HTTP
       |
       v
Transport Security
       |
       v
Authentication
       |
       v
MCPServer
       |
       v
RuntimeService
       |
       v
ROS Adapter
```

ROS adapter code must not contain HTTP authentication logic.

---

## 2.5 Bearer Authentication

The current implementation supports optional Bearer authentication.

The static Bearer token verifier is intended for controlled development, laboratory, and trusted-network deployments.

It must:

```text
reject missing tokens
reject incorrect tokens
accept the configured token
return the corresponding MCP AccessToken
```

Authentication secrets must not be committed to the repository.

---

## 2.6 Authentication Environment

Authentication-sensitive values must be supplied through runtime environment configuration.

They must not be stored directly in the packaged default TOML configuration.

The authentication implementation must fail safely when authentication is enabled but required authentication configuration is missing.

---

## 2.7 OAuth Protected Resource Metadata

Authenticated Streamable HTTP must expose OAuth Protected Resource Metadata.

For:

```text
/mcp
```

the path-specific metadata route is:

```text
/.well-known/oauth-protected-resource/mcp
```

Metadata includes:

```text
resource
authorization_servers
scopes_supported
bearer_methods_supported
```

The current MCP access scope is:

```text
ros2_mcp:access
```

---

## 2.8 HTTP MCP Protocol Metadata

The Streamable HTTP transport must preserve the MCP `2026-07-28` request metadata used by the MCP SDK.

Validated HTTP metadata includes:

```text
Mcp-Method
Mcp-Name
MCP-Protocol-Version
```

Validated MCP operations include:

```text
server/discover
tools/list
prompts/list
resources/templates/list
tools/call
resources/read
prompts/get
```

Regression tests must protect this behavior.

---

## 2.9 TLS Boundary

`ros2_mcp` does not implement a custom TLS stack.

For production remote deployment, TLS should be provided by infrastructure such as:

```text
reverse proxy
load balancer
Kubernetes ingress
service mesh
deployment gateway
```

Bearer authentication must not be treated as a replacement for transport encryption.

---

# 3. MCP Capability Requirements

## 3.1 MCP Tools

The current baseline is:

```text
46 MCP tools
```

Tools are appropriate for:

```text
runtime operations
explicit runtime inspection
state-changing operations
operations requiring structured arguments
```

Write-capable tools must remain subject to the runtime safety model.

---

## 3.2 MCP Prompts

The current baseline is:

```text
6 MCP prompts
```

Prompts must remain:

```text
client independent
LLM independent
transport independent
```

Prompts should guide clients in using existing MCP capabilities rather than bypassing the normal MCP architecture.

---

## 3.3 MCP Resources

The current baseline contains:

```text
0 static MCP resources
```

Resources are read-oriented.

They must not introduce hidden runtime state changes.

---

## 3.4 MCP Resource Templates

The current baseline is:

```text
9 resource templates
```

Parameterized runtime information should use Resource Templates rather than dynamically registering an unbounded number of static resources.

---

## 3.5 Server Instructions

Server Instructions should describe correct interaction with the ROS runtime.

Instructions must remain client independent.

Do not introduce instructions that require one specific MCP client unless there is a protocol-level requirement.

---

# 4. Scope Boundaries

## 4.1 Generic ROS 2 Scope

`ros2_mcp` is the generic ROS 2 runtime MCP server.

Generic ROS 2 functionality belongs here.

Examples include:

```text
nodes
topics
services
parameters
actions
interfaces
QoS
diagnostics
rosout
runtime health
process management
launch management
lifecycle
rosbag
```

---

## 4.2 Specialized Robotics Systems

Subsystem-specific semantics are intentionally outside the generic runtime scope.

This includes:

```text
ros2_control-specific semantics
Nav2-specific semantics
MoveIt 2-specific semantics
```

These systems can still be accessed through generic ROS 2 primitives where appropriate.

Dedicated subsystem MCP servers may be implemented separately.

---

## 4.3 Perception Boundary

The generic runtime may inspect ROS graph entities and topics associated with cameras or other sensors.

It is not required to provide specialized:

```text
image decoding
image rendering
depth processing
point-cloud perception
camera-specific configuration
visual inference
```

These belong to specialized perception components.

---

## 4.4 ROS 1 Boundary

ROS 1 is intentionally unsupported.

The architecture is designed for:

```text
ROS 2
DDS
rclpy
ROS 2 Actions
ROS 2 Lifecycle
ROS 2 QoS
ROS 2 interfaces
```

ROS 1 compatibility is not a release requirement.

---

# 5. Testing Requirements

## 5.1 Test Structure

The current test structure is:

```text
tests/
├── integration/
└── unit/
```

Unit tests should verify isolated application, configuration, safety, authentication, and helper behavior.

Integration tests should verify behavior crossing architectural boundaries.

---

## 5.2 Full Regression Test

Before committing changes:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
pytest --collect-only -q
git diff --check
```

The current validated baseline is:

```text
48 tests
```

---

## 5.3 MCP Inventory Verification

The current MCP inventory baseline is:

```text
46 tools
6 prompts
0 static resources
9 resource templates
```

A change must not unintentionally reduce these values.

---

## 5.4 HTTP Integration Tests

HTTP integration testing must cover:

```text
Streamable HTTP startup
MCP protocol negotiation
tool listing
prompt listing
Resource Template listing
tool invocation
resource reading
prompt retrieval
Host validation
Origin validation
```

---

## 5.5 Authentication Integration Tests

Authentication testing must cover:

```text
request without token
request with invalid token
request with valid token
authenticated MCP tool execution
OAuth Protected Resource Metadata
```

Expected authentication behavior:

```text
missing token -> HTTP 401
invalid token -> HTTP 401
valid token   -> MCP access
```

---

## 5.6 Protocol Metadata Tests

HTTP integration tests must verify MCP `2026-07-28` request metadata.

The regression suite must protect:

```text
Mcp-Method
Mcp-Name
MCP-Protocol-Version
```

---

# 6. Packaging Requirements

## 6.1 Package Build

The project must build successfully as:

```text
wheel
source distribution
```

Build with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf dist
uv build
```

---

## 6.2 Installed Entry Points

The installed package exposes:

```text
ros2-mcp
ros2-mcp-http
```

Both entry points must work outside the source repository when installed correctly.

---

## 6.3 Packaged Configuration

The installed package must include its own default configuration.

It must not require the source repository working directory to locate:

```text
default.toml
```

---

# 7. Requirements for Starting ros2_mcp

## 7.1 Development Environment

Before starting either transport:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Optional ROS runtime configuration:

```bash
export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

## 7.2 Start stdio

Start:

```bash
ros2-mcp
```

The transport is:

```text
stdio
```

---

## 7.3 Start Streamable HTTP

Start:

```bash
ros2-mcp-http
```

The default endpoint is:

```text
http://127.0.0.1:8000/mcp
```

Remote exposure requires explicit HTTP configuration.

---

## 7.4 Installed Package

ROS 2 must still be sourced before starting an installed package:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp
```

or:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp-http
```

---

# 8. MCP Client Requirements

An MCP client starting `ros2-mcp` must provide a valid ROS 2 environment.

The safest startup pattern is:

```bash
bash -lc 'source /opt/ros/jazzy/setup.bash && exec ros2-mcp'
```

If a dedicated virtual environment contains the executable:

```bash
bash -lc 'source /opt/ros/jazzy/setup.bash && exec /path/to/venv/bin/ros2-mcp'
```

The MCP server must remain client independent.

Codex is one supported client, not an architectural dependency.

---

# 9. Git Requirements

Before committing:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git status
git diff --check
pytest -q
```

The working tree should contain only intentional changes.

After committing:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git status
git log -3 --oneline --decorate
```

---

# 10. Branch Requirements

Normal development occurs on:

```text
dev
```

The release branch is:

```text
main
```

The normal release flow is:

```text
development
    |
    v
dev
    |
    | complete implementation
    | regression tests
    | documentation
    | packaging verification
    v
release validation
    |
    v
main
```

Normal release work must not bypass the validated `dev -> main` flow.

---

# 11. Release Requirements

Before promotion from `dev` to `main`:

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

The current release baseline is:

```text
ROS 2 Jazzy

Python 3.12

MCP Python SDK 2.0.0
MCP protocol 2026-07-28

46 MCP tools
6 MCP prompts
0 static resources
9 resource templates

stdio PASS
Streamable HTTP PASS

DNS rebinding protection PASS
Host validation PASS
Origin validation PASS

Bearer authentication PASS
OAuth Protected Resource Metadata PASS

48 automated tests PASS
```

---

# 12. Current Release Scope

The current `v0.1.0` release candidate includes:

```text
generic ROS 2 runtime access

ROS graph discovery
topics
services
parameters
actions
interfaces
QoS
diagnostics
rosout
runtime health

process management
launch management
lifecycle
rosbag

MCP tools
MCP prompts
MCP Resource Templates
Server Instructions

MCP 2026-07-28

stdio transport
Streamable HTTP transport

DNS rebinding protection
Host validation
Origin validation

optional Bearer authentication
OAuth Protected Resource Metadata

runtime safety
resource limits
dry-run support

packaged configuration
installable Python package
wheel and source distribution

ROS 2 Jazzy integration

48 automated tests
```

---

# 13. Intentional Non-Goals

The following are not requirements for the current generic `ros2_mcp` release:

```text
ROS 1

ros2_control-specific semantics
Nav2-specific semantics
MoveIt 2-specific semantics

camera-specific perception
LiDAR-specific perception

robot-specific application logic

arbitrary shell execution
arbitrary ROS CLI execution

production identity platform
custom TLS infrastructure
```

These are intentional architectural boundaries rather than missing generic ROS 2 runtime functionality.

---

# 14. Development Documentation

Detailed implementation history belongs under:

```text
docs/
```

The project phase documentation currently covers:

```text
Phase 1
Phase 2
Phase 3
Phase 4
Phase 5
Phase 6
Phase 7
Phase 8
Phase 9
Phase 10
Phase 11
Phase 12
Phase 13
Phase 14
```

Phase 14 documents:

```text
Remote MCP
Streamable HTTP
HTTP transport security
Bearer authentication
OAuth Protected Resource Metadata
remote MCP integration testing
```

The root `README.md` should describe the current project rather than duplicate detailed phase history.

---

# 15. Current Baseline

The current validated release candidate baseline is:

```text
Version:
v0.1.0 release candidate

Development branch:
dev

Release branch:
main

Operating system:
Ubuntu 24.04 LTS

ROS:
ROS 2 Jazzy

Python:
3.12

MCP SDK:
2.0.0

MCP protocol:
2026-07-28

MCP tools:
46

MCP prompts:
6

Static MCP resources:
0

MCP resource templates:
9

Local transport:
stdio

Remote transport:
Streamable HTTP

DNS rebinding protection:
PASS

Host validation:
PASS

Origin validation:
PASS

Bearer authentication:
PASS

OAuth Protected Resource Metadata:
PASS

Automated tests:
48 passed
```

The project is ready for final release validation before promotion from `dev` to `main`.
