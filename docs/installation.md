# ros2_mcp Installation

This guide describes how to install `ros2_mcp` from GitHub and connect it to an MCP-compatible client such as OpenAI Codex.

`ros2_mcp` supports two MCP transports:

- local MCP access through `stdio`
- remote MCP access through Streamable HTTP

The recommended starting point is the local `stdio` transport.

---

## 1. Requirements

Before installing `ros2_mcp`, the following software must already be installed:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.12
- Git
- `uv`
- OpenAI Codex CLI when using the Codex examples in this guide

Verify ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
echo "$ROS_DISTRO"
```

Expected:

```text
jazzy
```

Verify `uv`:

```bash
uv --version
```

Verify Git:

```bash
git --version
```

Verify Codex when it will be used as the MCP client:

```bash
codex --version
```

---

## 2. Download and Install ros2_mcp

Clone `ros2_mcp` from GitHub and install its Python environment:

```bash
cd ~/projects/robotics

git clone https://github.com/vagotec/ros2_mcp.git

cd ~/projects/robotics/ros2_mcp
uv sync

source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

`ros2_mcp` is now installed locally.

Verify the MCP executables:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

which ros2-mcp
which ros2-mcp-http
```

The executables should point into:

```text
~/projects/robotics/ros2_mcp/.venv/bin/
```

The two entry points are:

```text
ros2-mcp
    Local MCP server using stdio.

ros2-mcp-http
    MCP server using Streamable HTTP.
```

---

## 3. Verify the Installation

Verify the installed MCP SDK:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate

python - <<'PY'
from importlib.metadata import version

print("mcp:", version("mcp"))
PY
```

The currently validated project baseline uses:

```text
MCP Python SDK 2.0.0
```

Verify that ROS 2 Python support is available:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import rclpy

print("rclpy:", rclpy.__file__)
PY
```

---

## 4. Configure the ROS 2 Runtime

`ros2_mcp` must run inside a valid ROS 2 environment.

Before starting the server:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Optional ROS runtime variables can be configured when required:

```bash
export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

`ROS_DOMAIN_ID=30` is only an example.

Use the same ROS domain ID as the ROS 2 system that `ros2_mcp` should access.

---

## 5. Local MCP Access with stdio

The standard local server uses MCP over `stdio`.

Start it manually with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2-mcp
```

The architecture is:

```text
MCP Client
    |
    | MCP / stdio
    v
ros2-mcp
    |
    | rclpy
    v
ROS 2 Jazzy
```

Normally, an MCP client starts this process automatically.

When an MCP client owns the process, `ros2-mcp` does not need to be started manually in another terminal.

---

## 6. Add ros2_mcp to Codex

Register `ros2_mcp` as a local MCP server:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp add ros2_mcp \
  --env ROS_DOMAIN_ID=30 \
  --env RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -- \
  bash -lc 'source /opt/ros/jazzy/setup.bash && cd ~/projects/robotics/ros2_mcp && source .venv/bin/activate && exec ros2-mcp'
```

`ROS_DOMAIN_ID=30` is an example.

If the ROS 2 system uses another domain ID, replace `30` with the correct value.

Verify the registration:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2_mcp
```

---

## 7. Start Codex

Start Codex:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
```

Codex will automatically start `ros2_mcp` through MCP.

You do not need to start `ros2-mcp` manually in another terminal.

Inside Codex, check the MCP connection with:

```text
/mcp
```

`ros2_mcp` should appear as an available MCP server.

---

## 8. Test ros2_mcp with Codex

Inside Codex, enter:

```text
Use ros2_mcp and list all currently discovered ROS 2 nodes.
```

Codex should use the `ros2_mcp` MCP server and return the discovered ROS 2 nodes.

Another example:

```text
Use ros2_mcp and list all currently discovered ROS 2 topics.
```

Runtime health can be tested with:

```text
Use ros2_mcp and inspect the current ROS 2 runtime health.
```

For an explicit MCP-only test:

```text
Use only ros2_mcp.
Do not use shell commands.
Do not modify project files.

Inspect the current ROS 2 runtime health.
```

---

## 9. Remote MCP Access with Streamable HTTP

`ros2_mcp` also supports MCP Streamable HTTP.

The dedicated executable is:

```text
ros2-mcp-http
```

Start the HTTP server with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2-mcp-http
```

The default endpoint is:

```text
http://127.0.0.1:8000/mcp
```

The default loopback binding is intentional.

It prevents the MCP server from automatically being exposed to other machines on the network.

---

## 10. Verify the HTTP Server

After starting `ros2-mcp-http`, verify the listener in another terminal:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ss -ltnp | grep ':8000'
```

For the default configuration, the listener should be bound to:

```text
127.0.0.1:8000
```

---

## 11. HTTP Configuration

HTTP configuration is part of the normal `ros2_mcp` configuration.

Important settings include:

```text
host
port
path
enable_dns_rebinding_protection
allowed_hosts
allowed_origins
```

The default MCP HTTP path is:

```text
/mcp
```

The default host is:

```text
127.0.0.1
```

The default port is:

```text
8000
```

---

## 12. External Configuration

The packaged default configuration is:

```text
src/ros2_mcp/config/default.toml
```

An external configuration file can be selected through:

```text
ROS2_MCP_CONFIG
```

Example:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS2_MCP_CONFIG="$HOME/ros2_mcp.toml"

ros2-mcp-http
```

This allows deployment-specific HTTP settings without changing the packaged defaults.

---

## 13. LAN Access

Remote LAN access must be configured explicitly.

Example configuration:

```toml
[runtime]
read_topic_timeout_sec = 1.0

[http]
host = "192.168.2.182"
port = 8000
path = "/mcp"
enable_dns_rebinding_protection = true

allowed_hosts = [
    "192.168.2.182:8000",
    "msi:8000",
]

allowed_origins = [
    "http://192.168.2.182:8000",
    "http://msi:8000",
]
```

Save this configuration outside the packaged defaults, for example:

```text
$HOME/ros2_mcp_lan.toml
```

Start the server with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS2_MCP_CONFIG="$HOME/ros2_mcp_lan.toml"

ros2-mcp-http
```

Verify the listener:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ss -ltnp | grep ':8000'
```

The listener should now use the configured LAN address.

---

## 14. HTTP Transport Security

Streamable HTTP supports MCP transport security.

The implementation includes:

```text
DNS rebinding protection
allowed Host validation
allowed Origin validation
```

The validated rejection behavior is:

```text
Invalid Origin
    -> HTTP 403

Invalid Host
    -> HTTP 421
```

DNS rebinding protection should remain enabled for remote deployments.

---

## 15. Bearer Authentication

Streamable HTTP supports optional Bearer token authentication.

Authentication is intended for controlled remote access.

The request flow is:

```text
MCP Client
    |
    | Authorization: Bearer <token>
    v
Authentication
    |
    v
ros2-mcp-http
    |
    v
ROS 2
```

The validated behavior is:

```text
No token
    -> HTTP 401

Invalid token
    -> HTTP 401

Valid token
    -> MCP access allowed
```

Authentication-sensitive values should be provided through environment configuration and must not be committed to Git.

The current static Bearer token verifier is intended for controlled deployments and is not a replacement for a complete production identity platform.

---

## 16. OAuth Protected Resource Metadata

When HTTP authentication is enabled, `ros2_mcp` exposes OAuth Protected Resource Metadata.

For the MCP endpoint:

```text
/mcp
```

the metadata endpoint is:

```text
/.well-known/oauth-protected-resource/mcp
```

The metadata contains information including:

```text
resource
authorization_servers
scopes_supported
bearer_methods_supported
```

The current remote MCP scope is:

```text
ros2_mcp:access
```

---

## 17. MCP Protocol

The current validated MCP protocol baseline is:

```text
2026-07-28
```

Streamable HTTP has been validated for MCP operations including:

```text
server/discover
tools/list
prompts/list
resources/templates/list
tools/call
resources/read
prompts/get
```

The implementation uses the MCP SDK Streamable HTTP transport rather than a custom REST API.

---

## 18. Current MCP Inventory

The current validated MCP inventory is:

```text
MCP tools:            46
MCP prompts:          6
Static resources:     0
Resource templates:   9
```

The generic ROS 2 runtime functionality includes areas such as:

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

## 19. Run the Automated Tests

Run the complete regression suite:

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
48 passed
```

---

## 20. Build the Package

Build the wheel and source distribution:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf dist
uv build
```

The `dist/` directory should contain:

```text
*.whl
*.tar.gz
```

---

## 21. Installed Package Usage

An installed package exposes:

```text
ros2-mcp
ros2-mcp-http
```

ROS 2 still needs to be sourced before starting either server.

For stdio:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp
```

For Streamable HTTP:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp-http
```

The installed package contains its own packaged default configuration and does not require the source repository as its working directory.

---

## 22. Troubleshooting ROS Discovery

Before debugging MCP connectivity, verify ROS itself:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

echo "ROS_DISTRO=$ROS_DISTRO"
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"

ros2 node list
ros2 topic list
```

If ROS itself cannot discover the expected runtime, fix ROS discovery before debugging MCP.

---

## 23. Troubleshooting rclpy

Verify:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import rclpy

print(rclpy.__file__)
PY
```

If `rclpy` cannot be imported, fix the ROS environment before debugging `ros2_mcp`.

---

## 24. Troubleshooting Codex

Verify the MCP registration:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2_mcp
```

Inside Codex:

```text
/mcp
```

`ros2_mcp` should appear as an available MCP server.

---

## 25. Troubleshooting Streamable HTTP

Verify the HTTP listener:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ss -ltnp | grep ':8000'
```

Typical HTTP errors:

```text
401
    Authentication is required or the Bearer token is invalid.

403
    The Origin header is not allowed.

421
    The Host header is not allowed.
```

Check the active HTTP configuration when these errors occur.

---

## 26. Security Notes

`ros2_mcp` can expose operations that modify a live ROS 2 runtime.

Remote MCP access should therefore be treated as privileged robot access.

For remote deployments:

- keep DNS rebinding protection enabled
- restrict allowed hosts
- restrict allowed origins
- use authentication
- do not expose the endpoint directly to an untrusted network
- use TLS when traffic leaves a trusted network
- keep ROS runtime safety rules enabled
- use physical and robot-level safety independently of MCP security

Bearer authentication does not replace TLS.

---

## 27. Installation Complete

Local MCP connection:

```text
Codex / MCP Client
       |
       | MCP / stdio
       v
   ros2-mcp
       |
       | rclpy
       v
  ROS 2 Jazzy
       |
       v
ROS 2 Nodes / Topics / Services / Actions
```

Remote MCP connection:

```text
Remote MCP Client
       |
       | MCP / Streamable HTTP
       v
Transport Security
       |
       v
Authentication
       |
       v
 ros2-mcp-http
       |
       | rclpy
       v
  ROS 2 Jazzy
```

`ros2_mcp` is now ready for local MCP use and controlled remote MCP access.
