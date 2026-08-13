# ros2_mcp Installation

This guide describes how to install `ros2_mcp` from GitHub and connect it to OpenAI Codex.

## 1. Requirements

Before installing `ros2_mcp`, the following software must already be installed:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- OpenAI Codex CLI
- Git
- `uv`

Verify ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
echo "$ROS_DISTRO"
```

Expected:

```text
jazzy
```

Verify Codex:

```bash
codex --version
```

---

## 2. Download and install ros2_mcp

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

Verify the MCP executable:

```bash
which ros2-mcp
```

It should point to:

```text
~/projects/robotics/ros2_mcp/.venv/bin/ros2-mcp
```

---

## 3. Add ros2_mcp to Codex

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

If your ROS 2 system uses another domain ID, replace `30` with your ROS domain ID.

Verify the registration:

```bash
codex mcp get ros2_mcp
```

---

## 4. Start Codex

Start Codex:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
```

Codex will automatically start `ros2_mcp` through MCP.

You do not need to start `ros2-mcp` manually in another terminal.

---

## 5. Test ros2_mcp

Inside Codex, enter:

```text
Use ros2_mcp and list all currently discovered ROS 2 nodes.
```

Codex should use the `ros2_mcp` MCP server and return the discovered ROS 2 nodes.

Another example:

```text
Use ros2_mcp and list all currently discovered ROS 2 topics.
```

You can also check the MCP connection inside Codex with:

```text
/mcp
```

`ros2_mcp` should be shown as an available MCP server.

---

## Installation complete

The complete connection is now:

```text
Codex
  │
  │ MCP
  ▼
ros2_mcp
  │
  │ rclpy
  ▼
ROS 2 Jazzy
  │
  ▼
ROS 2 Nodes / Topics / Services / Actions
```

`ros2_mcp` is now ready to be used by Codex.
