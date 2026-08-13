# Phase 8 — Packaging, Configuration, Installation, and Deployment Readiness

## 1. Overview

Phase 8 prepares `ros2_mcp` for reliable use outside the source repository.

Phase 7 completed the ROS 2 runtime foundation and exposed 46 MCP tools.

Phase 8 focuses on the operational boundary around that runtime:

- robust configuration resolution
- centralized configuration ownership
- packaged default configuration
- Python wheel packaging
- isolated package installation
- execution outside the repository
- installed `ros2-mcp` CLI verification
- ROS 2 Jazzy environment compatibility
- real MCP stdio verification
- Codex integration with the installed package
- permanent configuration regression tests
- permanent MCP server lifespan regression testing

The primary goal is to remove the assumption that `ros2_mcp` must be executed from:

```text
~/projects/robotics/ros2_mcp
```

A correctly installed `ros2_mcp` package must be able to start from another working directory while still locating its configuration and using the ROS 2 environment correctly.

---

## 2. Phase 8 Goals

Phase 8 validates the following requirements.

### Configuration

`ros2_mcp` must:

- provide a packaged default configuration
- resolve configuration independently of the current working directory
- support an explicit configuration path
- support the `ROS2_MCP_CONFIG` environment variable
- reject invalid explicit configuration paths
- avoid hard-coded repository-relative configuration paths
- use the same configuration mechanism for runtime and safety settings

### Packaging

The Python package must:

- build as a wheel
- contain the packaged default configuration
- expose the `ros2-mcp` CLI entry point
- be installable into an isolated Python environment
- operate outside the source repository

### ROS 2

The installed package must:

- run with ROS 2 Jazzy
- import `rclpy`
- inherit the configured ROS domain
- support the configured RMW implementation

### MCP

The installed MCP server must:

- start through stdio
- expose all 46 runtime tools
- execute representative ROS 2 MCP operations
- preserve the Phase 7 safety model
- initialize and shut down its runtime correctly

### Codex

Codex must be able to connect to the installed package without depending on the source checkout.

---

## 3. Environment

Phase 8 was developed and verified with:

```text
Operating system: Ubuntu 24.04 LTS
ROS distribution: ROS 2 Jazzy
Python: 3.12
MCP Python SDK: >=2,<3
Package manager: uv
Codex CLI: 0.147.0
ROS_DOMAIN_ID: 30
RMW implementation: rmw_cyclonedds_cpp
```

Project directory:

```text
~/projects/robotics/ros2_mcp
```

Development virtual environment:

```text
~/projects/robotics/ros2_mcp/.venv
```

---

## 4. Phase 8 Architecture

Phase 8 adds installation and configuration infrastructure around the Phase 7 runtime.

```text
                       MCP Client
                           |
                           v
                     ros2-mcp CLI
                           |
                           v
                     create_server()
                           |
                           v
                      MCP lifespan
                           |
                           v
                 resolve_config_path()
                           |
              +------------+------------+
              |                         |
              v                         v
       ROS2_MCP_CONFIG          packaged default.toml
              |                         |
              +------------+------------+
                           |
                           v
                     load_settings()
                           |
               +-----------+-----------+
               |                       |
               v                       v
        RuntimeSettings          SafetySettings
               |                       |
               +-----------+-----------+
                           |
                           v
                    JazzyRosAdapter
                           |
                           v
                     RuntimeService
                           |
                           v
                      46 MCP tools
                           |
                           v
                      ROS 2 Jazzy
```

The current working directory is no longer responsible for locating the runtime configuration.

---

# 5. Configuration Architecture

The configuration implementation is located under:

```text
src/ros2_mcp/config/
```

The packaged default configuration is:

```text
src/ros2_mcp/config/default.toml
```

Configuration resolution and loading are implemented in:

```text
src/ros2_mcp/config/settings.py
```

The server obtains its configuration through the centralized resolver.

Runtime modules must not independently construct repository-relative paths such as:

```text
config/ros2_mcp.toml
```

---

## 6. Configuration Resolution

Configuration resolution is centralized through:

```python
resolve_config_path()
```

The resolver supports three configuration sources.

### 6.1 Explicit configuration path

An explicit configuration path may be supplied programmatically.

This is useful for:

- tests
- embedded usage
- controlled deployments
- custom runtime environments

### 6.2 Environment override

The supported environment variable is:

```text
ROS2_MCP_CONFIG
```

Example:

```bash
export ROS2_MCP_CONFIG=/etc/ros2_mcp/production.toml
```

This allows deployment-specific configuration without modifying the installed package.

### 6.3 Packaged default

If no explicit configuration is supplied, the package uses:

```text
ros2_mcp/config/default.toml
```

from the installed Python package.

This makes configuration independent of the current working directory.

---

## 7. Configuration Precedence

The configuration precedence is:

```text
explicit configuration path
            |
            v
     ROS2_MCP_CONFIG
            |
            v
  packaged default.toml
```

An explicitly requested configuration file must exist.

An invalid explicit configuration path is rejected instead of silently falling back to another configuration.

This prevents configuration mistakes from being hidden during deployment.

---

## 8. Packaged Default Configuration

The package contains:

```text
src/ros2_mcp/config/default.toml
```

The default configuration contains runtime and safety settings required by the server.

After wheel installation, the configuration is located under a path similar to:

```text
<venv>/lib/python3.12/site-packages/ros2_mcp/config/default.toml
```

This location was verified using an isolated installation.

---

## 9. Runtime Configuration

The current runtime configuration contains:

```text
read_topic_timeout_sec
```

The verified default value is:

```text
1.0
```

The corresponding runtime object is:

```text
RuntimeSettings(read_topic_timeout_sec=1.0)
```

Additional runtime settings can be added to this centralized configuration model in future phases.

---

## 10. Safety Configuration

The safety policy uses the same centralized configuration system.

The safety adapter no longer owns a separate repository-relative configuration path.

The verified safety model includes:

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

Protected default topics include:

```text
/parameter_events
/rosout
```

Default resource limits include:

```text
persistent publishers: 32
managed processes:      16
managed launches:       8
bag recordings:         4
bag playbacks:          4
```

Dry-run support is available for:

```text
start_ros_process
start_ros_launch
start_bag_recording
start_bag_playback
```

---

# 11. Central Configuration Ownership

Runtime Python modules must not independently construct the old repository configuration path.

The following command checks for regression:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

grep -Rni \
  'config/ros2_mcp.toml' \
  src/ros2_mcp \
  --include='*.py' \
  --exclude-dir='__pycache__'
```

Expected result:

```text
No hard-coded config/ros2_mcp.toml references.
```

Configuration ownership belongs to:

```text
ros2_mcp.config.settings
```

---

# 12. Server Lifespan

The MCP server lifespan initializes and cleans up the runtime.

The tested lifecycle is:

```text
create_server()
      |
      v
MCP lifespan
      |
      v
resolve_config_path()
      |
      v
load_settings()
      |
      v
JazzyRosAdapter
      |
      v
RuntimeService
      |
      v
AppContext
      |
      v
MCP tool execution
      |
      v
clean shutdown
```

This lifecycle is covered by a permanent integration test.

---

# 13. Python Package Metadata

The project is defined in:

```text
pyproject.toml
```

The package metadata includes:

```toml
[project]
name = "ros2-mcp"
version = "0.1.0"
description = "A modular MCP server for ROS 2 runtime inspection, monitoring, and controlled interaction."
requires-python = ">=3.12,<3.13"
dependencies = [
    "mcp>=2,<3",
]
```

The command-line entry point is:

```toml
[project.scripts]
ros2-mcp = "ros2_mcp.server:main"
```

The build backend is:

```toml
[build-system]
requires = ["uv_build>=0.11.32,<0.12.0"]
build-backend = "uv_build"
```

---

# 14. CLI Entry Point

After installation, the MCP server is started through:

```text
ros2-mcp
```

The entry point resolves to:

```text
ros2_mcp.server:main
```

In the project virtual environment it resolves to:

```text
~/projects/robotics/ros2_mcp/.venv/bin/ros2-mcp
```

In an isolated installation it resolves to:

```text
<isolated-venv>/bin/ros2-mcp
```

---

# 15. Development Environment Startup

Always initialize the development environment with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Verify it with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

which python
python --version

echo "ROS_DISTRO=$ROS_DISTRO"
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
echo "AMENT_PREFIX_PATH=$AMENT_PREFIX_PATH"
echo "PYTHONPATH=$PYTHONPATH"
```

Expected ROS distribution:

```text
jazzy
```

---

# 16. Start the MCP Server from Source

Start through the CLI:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2-mcp
```

The module entry point may also be used during development:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m ros2_mcp.server
```

The installed CLI should be preferred for package installation verification.

---

# 17. ROS Python Environment

ROS 2 Jazzy provides `rclpy` through:

```text
/opt/ros/jazzy/lib/python3.12/site-packages
```

Verify the Python and ROS environments with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import sys
import rclpy

print("Python:", sys.executable)
print("rclpy:", rclpy.__file__)

print()
print("sys.path:")

for path in sys.path:
    print(path)
PY
```

The Python executable should be:

```text
~/projects/robotics/ros2_mcp/.venv/bin/python
```

`rclpy` should come from the ROS 2 Jazzy installation.

---

# 18. ROS Environment Variables

Important ROS runtime variables include:

```text
ROS_DISTRO
ROS_DOMAIN_ID
RMW_IMPLEMENTATION
AMENT_PREFIX_PATH
PYTHONPATH
LD_LIBRARY_PATH
PATH
ROS_PYTHON_VERSION
```

The verified project configuration uses:

```text
ROS_DISTRO=jazzy
ROS_DOMAIN_ID=30
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

The complete ROS environment should be initialized through:

```bash
source /opt/ros/jazzy/setup.bash
```

---

# 19. Verify Configuration Resolution

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from ros2_mcp.config.settings import (
    load_settings,
    resolve_config_path,
)

config_path = resolve_config_path()

print("Resolved config:")
print(config_path)

print()
print("Exists:")
print(config_path.exists())

print()
print("Settings:")
print(load_settings(config_path))
PY
```

The default configuration should resolve to:

```text
src/ros2_mcp/config/default.toml
```

when running from the development checkout.

---

# 20. Verify Invalid Explicit Configuration

An explicitly configured missing file must be rejected.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ROS2_MCP_CONFIG=/tmp/ros2-mcp-config-does-not-exist.toml \
python - <<'PY'
from ros2_mcp.config.settings import resolve_config_path

try:
    resolve_config_path()
except FileNotFoundError as exc:
    print("Invalid explicit config rejected:")
    print(exc)
    print("INVALID CONFIG: PASS")
else:
    raise SystemExit(
        "Expected FileNotFoundError was not raised."
    )
PY
```

Expected result:

```text
INVALID CONFIG: PASS
```

---

# 21. Build the Package

The project uses `uv_build`.

Build the source distribution and wheel with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf dist

uv build

ls -lh dist
```

Expected artifacts include:

```text
*.tar.gz
*.whl
```

---

# 22. Inspect the Wheel

Verify that the wheel contains the packaged configuration:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from pathlib import Path
from zipfile import ZipFile

wheels = sorted(Path("dist").glob("*.whl"))

if not wheels:
    raise SystemExit("No wheel found.")

wheel = wheels[-1]

print("Wheel:")
print(wheel)

with ZipFile(wheel) as archive:
    names = archive.namelist()

    configs = [
        name
        for name in names
        if name.endswith(
            "ros2_mcp/config/default.toml"
        )
    ]

    print()
    print("Packaged default config:")
    print(configs)

    if not configs:
        raise SystemExit(
            "default.toml is missing from the wheel."
        )

print()
print("WHEEL CONFIG CHECK: PASS")
PY
```

Expected result:

```text
WHEEL CONFIG CHECK: PASS
```

---

# 23. Inspect the CLI Entry Point in the Wheel

The installed package must expose:

```text
ros2-mcp
```

which resolves to:

```text
ros2_mcp.server:main
```

After installation this can be inspected with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
from importlib.metadata import entry_points

matches = [
    entry
    for entry in entry_points(group="console_scripts")
    if entry.name == "ros2-mcp"
]

for entry in matches:
    print(
        f"{entry.name} -> {entry.value}"
    )

if not matches:
    raise SystemExit(
        "ros2-mcp console entry point not found."
    )
PY
```

Expected mapping:

```text
ros2-mcp -> ros2_mcp.server:main
```

---

# 24. Create an Isolated Installation

A clean virtual environment verifies that the package does not depend on the source checkout.

Example:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

rm -rf /tmp/ros2_mcp_phase_8_test_venv

python -m venv \
  --system-site-packages \
  /tmp/ros2_mcp_phase_8_test_venv

/tmp/ros2_mcp_phase_8_test_venv/bin/pip install \
  dist/*.whl
```

`--system-site-packages` is important in this ROS 2 Jazzy environment because `rclpy` is supplied by the ROS Debian installation rather than being declared as a normal PyPI dependency of `ros2_mcp`.

---

# 25. Verify the Installed Package from `/tmp`

Run the verification outside the repository:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

cd /tmp

/tmp/ros2_mcp_phase_8_test_venv/bin/python - <<'PY'
import ros2_mcp
import rclpy

from ros2_mcp.config.settings import (
    load_settings,
    resolve_config_path,
)

print("ros2_mcp:")
print(ros2_mcp.__file__)

print()
print("rclpy:")
print(rclpy.__file__)

config_path = resolve_config_path()

print()
print("Installed config:")
print(config_path)

print()
print("Exists:")
print(config_path.exists())

print()
print("Settings:")
print(load_settings(config_path))
PY

cd ~/projects/robotics/ros2_mcp
```

The configuration must resolve into the installed package under:

```text
/tmp/ros2_mcp_phase_8_test_venv/lib/python3.12/site-packages/ros2_mcp/config/default.toml
```

and not into the source repository.

---

# 26. Verify `rclpy` from the Isolated Environment

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

/tmp/ros2_mcp_phase_8_test_venv/bin/python - <<'PY'
import sys
import rclpy

print("Python:")
print(sys.executable)

print()
print("rclpy:")
print(rclpy.__file__)
PY
```

Expected Python:

```text
/tmp/ros2_mcp_phase_8_test_venv/bin/python
```

Expected `rclpy` source:

```text
/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/
```

---

# 27. Verify the Installed CLI

Run from `/tmp`:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

cd /tmp

which /tmp/ros2_mcp_phase_8_test_venv/bin/ros2-mcp

/tmp/ros2_mcp_phase_8_test_venv/bin/python - <<'PY'
from importlib.metadata import entry_points

matches = [
    entry
    for entry in entry_points(group="console_scripts")
    if entry.name == "ros2-mcp"
]

for entry in matches:
    print(
        f"{entry.name} -> {entry.value}"
    )
PY

cd ~/projects/robotics/ros2_mcp
```

Expected mapping:

```text
ros2-mcp -> ros2_mcp.server:main
```

---

# 28. Real Installed MCP stdio Verification

The installed package must be verified through the actual MCP stdio protocol.

Example:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

cd /tmp

/tmp/ros2_mcp_phase_8_test_venv/bin/python - <<'PY'
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    env = dict(os.environ)

    server = StdioServerParameters(
        command=(
            "/tmp/ros2_mcp_phase_8_test_venv/"
            "bin/ros2-mcp"
        ),
        env=env,
    )

    async with stdio_client(server) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            tools = await session.list_tools()

            names = {
                tool.name
                for tool in tools.tools
            }

            print("Tool count:", len(names))

            required = {
                "list_nodes",
                "list_topics",
                "list_actions",
                "interface_info",
                "get_runtime_health",
                "get_safety_guardrails",
                "start_ros_process",
            }

            missing = sorted(
                required - names
            )

            print(
                "Required tools missing:",
                missing,
            )

            if len(names) != 46:
                raise RuntimeError(
                    f"Expected 46 tools, got {len(names)}."
                )

            if missing:
                raise RuntimeError(
                    f"Missing tools: {missing}"
                )

            print(
                "REAL INSTALLED MCP STDIO: PASS"
            )


asyncio.run(main())
PY

cd ~/projects/robotics/ros2_mcp
```

Expected result:

```text
Tool count: 46
Required tools missing: []
REAL INSTALLED MCP STDIO: PASS
```

---

# 29. Verify Installed Safety Configuration through MCP

The installed MCP server must be able to execute the safety tool.

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

cd /tmp

/tmp/ros2_mcp_phase_8_test_venv/bin/python - <<'PY'
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server = StdioServerParameters(
        command=(
            "/tmp/ros2_mcp_phase_8_test_venv/"
            "bin/ros2-mcp"
        ),
        env=dict(os.environ),
    )

    async with stdio_client(server) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            result = await session.call_tool(
                "get_safety_guardrails",
                {},
            )

            print(
                "is_error:",
                result.is_error,
            )

            print(
                "Content blocks:",
                len(result.content),
            )

            if result.is_error:
                raise RuntimeError(
                    "Safety MCP call failed."
                )

            if not result.content:
                raise RuntimeError(
                    "Safety MCP result is empty."
                )

            print(
                "SAFETY MCP CALL: PASS"
            )


asyncio.run(main())
PY

cd ~/projects/robotics/ros2_mcp
```

Expected result:

```text
is_error: False
SAFETY MCP CALL: PASS
```

---

# 30. Codex Installed-Package Architecture

Phase 8 verifies the following path:

```text
Codex CLI
    |
    | MCP stdio
    v
ros2_mcp_installed
    |
    v
isolated virtual environment
    |
    v
ros2-mcp
    |
    v
installed ros2_mcp package
    |
    v
packaged default.toml
    |
    v
ROS 2 Jazzy
```

This test deliberately avoids executing `ros2_mcp` directly from the development source checkout.

---

# 31. Verify Codex Version

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex --version
```

Phase 8 was verified with:

```text
codex-cli 0.147.0
```

---

# 32. Inspect Existing Codex MCP Configuration

Before adding the isolated server:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp list
```

The existing development registration may still be present as:

```text
ros2_mcp
```

The isolated test uses a separate name:

```text
ros2_mcp_installed
```

This prevents the test from modifying the development registration.

---

# 33. Register the Installed MCP Server with Codex

The Phase 8 isolated verification environment used:

```text
/tmp/ros2_mcp_phase_8_3_final_venv
```

Before registration, verify that the installed executable exists:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ISOLATED_MCP="/tmp/ros2_mcp_phase_8_3_final_venv/bin/ros2-mcp"

test -x "$ISOLATED_MCP"

echo "$ISOLATED_MCP"
```

Remove an older temporary registration if one exists:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp remove ros2_mcp_installed 2>/dev/null || true
```

Register the installed server:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp add ros2_mcp_installed \
  --env ROS_DOMAIN_ID=30 \
  --env RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -- \
  bash -lc \
  'source /opt/ros/jazzy/setup.bash && exec /tmp/ros2_mcp_phase_8_3_final_venv/bin/ros2-mcp'
```

The important property is that the command executes:

```text
/tmp/ros2_mcp_phase_8_3_final_venv/bin/ros2-mcp
```

and does not execute:

```text
python -m ros2_mcp.server
```

from the source repository.

---

# 34. Inspect the Codex Installed MCP Registration

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2_mcp_installed

echo

codex mcp list
```

The registration should show:

```text
ros2_mcp_installed
enabled: true
transport: stdio
```

The command should ultimately execute:

```text
/tmp/ros2_mcp_phase_8_3_final_venv/bin/ros2-mcp
```

---

# 35. Verify the Development MCP Registration Was Not Changed

Run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp get ros2_mcp
```

The development registration and installed-package test registration remain separate:

```text
ros2_mcp
ros2_mcp_installed
```

---

# 36. Start Codex for the Installed-Package Test

Start Codex from the ROS environment:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex
```

The installed-package test must use only:

```text
ros2_mcp_installed
```

---

# 37. Final Codex Installed-Package Test Prompt

Use the following prompt inside Codex:

```text
Use only ros2_mcp_installed.

Perform a final end-to-end verification of the installed ros2_mcp package.

IMPORTANT:
- Use ros2_mcp_installed only.
- Do not use ros2_mcp.
- Do not use ros2_dev_mcp.
- Do not use shell commands.
- Do not modify files.
- Do not start any real ROS process.
- Any process start verification must use dry_run=true.

Perform these checks:

1. List all currently discovered ROS 2 nodes.

2. List all currently discovered ROS 2 topics.

3. List all currently discovered ROS 2 actions.

4. Inspect the ROS interface:
   std_msgs/msg/String

5. List installed action interfaces from package:
   example_interfaces

6. Show the current runtime health summary.

7. Show the active safety guardrails.

8. Dry-run starting:
   package: demo_nodes_cpp
   executable: talker

9. Verify that the installed MCP server exposes and can execute
   representative tools from these functional areas:
   - graph discovery
   - topics
   - actions
   - interface discovery
   - diagnostics/runtime health
   - safety
   - controlled process management

At the end provide a verification summary containing:

- MCP server used
- tools used
- node discovery result
- topic discovery result
- action discovery result
- std_msgs/msg/String inspection result
- example_interfaces action discovery result
- runtime health result
- safety guardrail result
- process dry-run result
- whether any real process was started
- whether any file was modified
- whether every requested operation succeeded

If an operation fails, do not hide or work around the failure.
Report the exact failing ros2_mcp_installed tool and the error.
```

---

# 38. Final Codex Verification Results

The final installed-package verification successfully used:

```text
ros2_mcp_installed
```

Tools executed:

```text
list_nodes
list_topics
list_actions
interface_info
list_interfaces
get_runtime_health
get_safety_guardrails
start_ros_process
```

All requested operations succeeded.

No shell command was used by Codex for the runtime verification.

No project file was modified.

No real ROS process was started.

---

# 39. Node Discovery Result

The installed MCP server successfully discovered the active ROS graph.

The final test discovered the ROS CLI daemon.

The exact node list is runtime-dependent and is not expected to remain constant between executions.

Result:

```text
node discovery: PASS
```

---

# 40. Topic Discovery Result

The installed server successfully discovered ROS topics.

The final isolated verification included:

```text
/parameter_events
/rosout
```

The exact topic list depends on the currently active ROS graph.

Result:

```text
topic discovery: PASS
```

---

# 41. Action Discovery Result

No action server was active during the final installed-package Codex test.

Therefore the active action list was empty.

This is not a failure.

Result:

```text
action discovery operation: PASS
active actions: none
```

Earlier Phase 7 runtime verification successfully discovered:

```text
/mcp_final/fibonacci
```

with:

```text
example_interfaces/action/Fibonacci
```

---

# 42. Interface Discovery Result

The installed package successfully inspected:

```text
std_msgs/msg/String
```

Result:

```text
package: std_msgs
kind: msg
interface: String
```

Field:

```text
data: string
```

Result:

```text
interface discovery: PASS
```

---

# 43. Installed Action Interface Discovery

The installed package successfully discovered action interfaces from:

```text
example_interfaces
```

Result:

```text
example_interfaces/action/Fibonacci
```

This verifies installed interface discovery independently of whether an action server is currently active.

Result:

```text
action interface discovery: PASS
```

---

# 44. Runtime Health Result

The installed-package Codex verification returned:

```text
health: OK
```

The runtime health summary includes:

```text
graph
diagnostics
rosout
```

The exact node, topic, and service counts are runtime snapshots and may change between calls.

Result:

```text
runtime health: PASS
```

---

# 45. Safety Guardrail Result

The installed package successfully loaded and exposed the packaged safety policy.

Verified properties included:

```text
arbitrary shell disabled
managed process stop only
managed launch stop only
managed rosbag stop only
package resolution required
launch-file resolution required
managed-name path traversal disabled
structured argument validation enabled
```

Protected topics included:

```text
/parameter_events
/rosout
```

Result:

```text
safety configuration: PASS
```

---

# 46. Controlled Process Dry-Run

The installed package successfully resolved:

```text
package: demo_nodes_cpp
executable: talker
```

The executable resolved to:

```text
/opt/ros/jazzy/lib/demo_nodes_cpp/talker
```

The operation was executed with:

```text
dry_run=true
```

Result:

```text
process resolution: PASS
real process started: NO
```

---

# 47. Remove the Temporary Codex Registration

The `/tmp` installation is a verification environment and is not intended to be permanent.

After the installed-package test, the temporary Codex registration can be removed with:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp remove ros2_mcp_installed

codex mcp list
```

This does not remove or modify the development registration:

```text
ros2_mcp
```

---

# 48. Permanent Configuration Regression Tests

Phase 8 adds:

```text
tests/unit/test_settings.py
```

The configuration tests cover:

```text
packaged default resolution
explicit path precedence
environment override
missing explicit configuration
missing environment configuration
default settings loading
custom settings loading
invalid limit validation
```

Eight permanent configuration tests were added.

---

# 49. Configuration Test Inventory

The configuration regression suite contains:

```text
test_resolve_config_path_uses_packaged_default
test_resolve_config_path_prefers_explicit_path
test_resolve_config_path_uses_environment_override
test_resolve_config_path_rejects_missing_explicit_path
test_resolve_config_path_rejects_missing_environment_override
test_load_packaged_default_settings
test_load_custom_settings
test_load_settings_rejects_non_positive_limit
```

These tests protect the package against regression to repository-relative configuration loading.

---

# 50. Run Configuration Tests Only

Use:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q tests/unit/test_settings.py
```

Expected result:

```text
8 passed
```

---

# 51. Permanent Server Lifespan Test

Phase 8 adds:

```text
tests/integration/test_server_lifespan.py
```

The test enters the real MCP server lifespan using:

```python
server = create_server()
```

and:

```python
async with Client(
    server,
    raise_exceptions=True,
) as client:
```

The test verifies:

```text
server startup
configuration loading
runtime initialization
46-tool inventory
safety tool execution
runtime-health execution
controlled process dry-run
clean lifespan shutdown
```

---

# 52. Lifespan Tool Inventory Verification

The lifespan test verifies exactly:

```text
46 tools
```

Representative required tools include:

```text
list_nodes
list_topics
list_actions
read_topic
read_topic_messages
get_runtime_health
get_safety_guardrails
start_ros_process
```

This provides permanent protection against accidental loss of major runtime functionality during future refactoring.

---

# 53. Lifespan Safety Verification

The lifespan integration test executes:

```text
get_safety_guardrails
```

and requires:

```text
is_error == false
```

The returned MCP content must also be non-empty.

This verifies that safety configuration is available after real server initialization.

---

# 54. Lifespan Runtime Health Verification

The integration test executes:

```text
get_runtime_health
```

and requires successful MCP execution.

This exercises several layers together:

```text
MCP
  |
  v
RuntimeService
  |
  v
JazzyRosAdapter
  |
  +--> ROS graph
  |
  +--> diagnostics
  |
  +--> rosout
```

---

# 55. Lifespan Controlled Process Verification

The integration test executes:

```text
start_ros_process
```

with:

```text
package_name = demo_nodes_cpp
executable = talker
dry_run = true
```

This verifies:

```text
package resolution
executable resolution
safety validation
MCP serialization
```

without starting a real process.

---

# 56. Run the Server Lifespan Test Only

Use:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q tests/integration/test_server_lifespan.py
```

Expected result:

```text
1 passed
```

---

# 57. Complete Phase 8 Test Suite

At the end of Phase 8, the complete regression suite contains:

```text
20 tests
```

The verified result is:

```text
20 passed
```

The suite contains:

```text
integration tests
unit tests
configuration tests
server lifecycle tests
runtime service tests
MCP runtime tests
adapter tests
```

---

# 58. Current Test Inventory

The Phase 8 test collection contains:

```text
tests/integration/test_jazzy_adapter.py::test_list_nodes_hides_internal_node
tests/integration/test_mcp_runtime_tool.py::test_runtime_tools_through_mcp
tests/integration/test_server_lifespan.py::test_server_lifespan_initializes_runtime_and_tools

tests/unit/test_runtime_service.py::test_list_nodes_uses_ros_adapter
tests/unit/test_runtime_service.py::test_list_topics_uses_ros_adapter
tests/unit/test_runtime_service.py::test_topic_info_uses_ros_adapter
tests/unit/test_runtime_service.py::test_list_services_uses_ros_adapter
tests/unit/test_runtime_service.py::test_read_topic_uses_ros_adapter
tests/unit/test_runtime_service.py::test_list_actions_uses_ros_adapter
tests/unit/test_runtime_service.py::test_action_info_uses_ros_adapter
tests/unit/test_runtime_service.py::test_read_topic_messages_uses_ros_adapter

tests/unit/test_server.py::test_create_server_returns_mcp_server

tests/unit/test_settings.py::test_resolve_config_path_uses_packaged_default
tests/unit/test_settings.py::test_resolve_config_path_prefers_explicit_path
tests/unit/test_settings.py::test_resolve_config_path_uses_environment_override
tests/unit/test_settings.py::test_resolve_config_path_rejects_missing_explicit_path
tests/unit/test_settings.py::test_resolve_config_path_rejects_missing_environment_override
tests/unit/test_settings.py::test_load_packaged_default_settings
tests/unit/test_settings.py::test_load_custom_settings
tests/unit/test_settings.py::test_load_settings_rejects_non_positive_limit
```

---

# 59. Run the Complete Test Suite

Use:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q
```

Expected Phase 8 result:

```text
20 passed
```

---

# 60. Verify Test Collection

Use:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest --collect-only -q
```

Expected result:

```text
20 tests collected
```

---

# 61. Python Syntax Verification

Use:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
```

Expected result:

```text
no syntax errors
```

---

# 62. Git Diff Quality Verification

Before committing:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git diff --check
```

Expected exit code:

```text
0
```

---

# 63. Current MCP Tool Inventory

Phase 8 does not add or remove runtime MCP functionality from Phase 7.

The installed server exposes:

```text
46 MCP tools
```

Current inventory:

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

---

# 64. Phase 8 Modified Files

The core Phase 8 changes include:

```text
src/ros2_mcp/config/settings.py
src/ros2_mcp/config/default.toml
src/ros2_mcp/ros/jazzy/safety.py
src/ros2_mcp/server.py
tests/unit/test_settings.py
tests/integration/test_server_lifespan.py
docs/README_PHASE_8.md
```

The main project `README.md` is updated separately to reflect the completed Phase 8 state.

---

# 65. Phase 8 Validation Matrix

| Area | Verification | Result |
|---|---|---|
| Configuration resolver | packaged default | PASS |
| Configuration resolver | explicit path | PASS |
| Configuration resolver | environment override | PASS |
| Configuration resolver | invalid explicit path | PASS |
| Configuration ownership | centralized | PASS |
| Packaged config | installed wheel | PASS |
| Runtime settings | packaged config | PASS |
| Safety settings | packaged config | PASS |
| Repository independence | execution from `/tmp` | PASS |
| ROS Python | `rclpy` import | PASS |
| CLI | installed `ros2-mcp` | PASS |
| MCP stdio | installed package | PASS |
| Tool inventory | 46 tools | PASS |
| Codex | installed MCP server | PASS |
| Graph discovery | installed MCP | PASS |
| Topics | installed MCP | PASS |
| Actions | installed MCP | PASS |
| Interfaces | installed MCP | PASS |
| Runtime health | installed MCP | PASS |
| Safety | installed MCP | PASS |
| Process management | dry-run | PASS |
| Server lifespan | integration test | PASS |
| Configuration tests | 8 tests | PASS |
| Complete regression suite | 20 tests | PASS |
| Python syntax | compileall | PASS |
| Diff quality | `git diff --check` | PASS |

---

# 66. What Phase 8 Solves

Before Phase 8, starting the server from the source repository could hide deployment problems.

For example:

```text
current working directory
          |
          v
 config/ros2_mcp.toml
```

works only while the expected repository structure is present.

Phase 8 replaces that assumption with:

```text
installed package
      |
      v
configuration resolver
      |
      +--> explicit configuration
      |
      +--> ROS2_MCP_CONFIG
      |
      +--> packaged default.toml
```

This is significantly more robust for:

```text
Codex
other MCP clients
isolated virtual environments
wheel installations
system services
containers
future Kubernetes deployments
```

---

# 67. Source Checkout vs Installed Package

Development can continue to use the editable source environment.

Deployment verification must distinguish between:

```text
source checkout
```

and:

```text
installed package
```

Phase 8 explicitly tests both.

A package may work from the repository while failing after installation because of:

```text
missing package data
relative paths
missing entry points
environment assumptions
undeclared dependencies
```

The isolated installation tests are designed to expose those problems.

---

# 68. ROS 2 Dependency Model

`rclpy` is supplied by the ROS 2 Jazzy installation.

It is not treated as an ordinary PyPI dependency of `ros2_mcp`.

The ROS environment remains an external runtime prerequisite.

```text
Ubuntu 24.04
     |
     +-----------------------------+
     |                             |
     v                             v
ROS 2 Jazzy                 Python environment
     |                             |
     +-- rclpy                     +-- ros2_mcp
     +-- ros2cli                   +-- MCP SDK
     +-- interfaces
     +-- RMW implementation
```

This separation is intentional.

---

# 69. MCP Dependency Model

The Python package declares:

```text
mcp>=2,<3
```

The MCP layer remains separated from the ROS adapter architecture.

```text
MCP client
    |
    v
MCP tools
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
ROS 2
```

Packaging does not remove this abstraction boundary.

---

# 70. Jazzy Adapter Isolation

ROS 2 Jazzy-specific functionality remains under:

```text
src/ros2_mcp/ros/jazzy/
```

The generic adapter contract remains under:

```text
src/ros2_mcp/ros/adapter.py
```

A future ROS distribution can conceptually use:

```text
ros/
├── adapter.py
├── jazzy/
└── <future-distribution>/
```

without changing the MCP-facing architecture.

---

# 71. Phase 8 Safety Principle

Packaging must not weaken runtime safety.

The installed package preserves the Phase 7 safety rules:

```text
no arbitrary shell execution
structured process arguments
package resolution required
launch-file resolution required
protected ROS resources
managed-resource stop restrictions
resource limits
dry-run support
```

The installed-package Codex verification confirms that these guardrails remain available through MCP.

---

# 72. Deployment Principle

`ros2_mcp` should be treated as a ROS-aware Python application.

A deployment needs:

```text
ROS environment
+
Python ros2_mcp environment
```

The ROS environment must be initialized before the MCP server starts.

For ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
```

The installed MCP executable can then be started.

---

# 73. Example Installed Startup

Example:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

/path/to/venv/bin/ros2-mcp
```

No repository `cd` is required.

This is one of the main Phase 8 improvements.

---

# 74. Example Custom Configuration

A deployment can use its own configuration:

```bash
source /opt/ros/jazzy/setup.bash

export ROS2_MCP_CONFIG=/etc/ros2_mcp/production.toml
export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

/path/to/venv/bin/ros2-mcp
```

This keeps deployment-specific policy outside the installed Python package.

---

# 75. Temporary Verification Environment

The Phase 8 isolated Codex verification used:

```text
/tmp/ros2_mcp_phase_8_3_final_venv
```

This path is intentionally temporary.

It must not be treated as a permanent deployment location.

Its purpose is to prove that the wheel works independently of:

```text
~/projects/robotics/ros2_mcp
```

---

# 76. Why `/tmp` Was Used

Testing from `/tmp` deliberately removes the repository working-directory assumption.

It answers the question:

```text
Does ros2_mcp work because it is correctly packaged,
or only because the process is running inside the source repository?
```

Phase 8 demonstrates that the installed package works independently of the repository working directory.

---

# 77. Phase 8 Regression Protection

The new tests should detect future regressions such as:

```text
removing default.toml from package behavior
breaking configuration precedence
silently accepting missing explicit configs
reintroducing repository-relative config paths
breaking MCP lifespan initialization
losing major MCP tools
breaking safety initialization
breaking runtime-health initialization
breaking process dry-run resolution
```

---

# 78. Final Phase 8 Quality Check

Before committing Phase 8, run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

printf '\n============================================================\n'
printf 'PHASE 8 - FINAL QUALITY CHECK\n'
printf '============================================================\n'

printf '\n--- Git status ---\n'
git status --short

printf '\n--- Python syntax ---\n'
python -m compileall -q src tests
SYNTAX_RC=$?

printf '\n--- Full test suite ---\n'
pytest -q
PYTEST_RC=$?

printf '\n--- Test collection ---\n'
pytest --collect-only -q
COLLECT_RC=$?

printf '\n--- Diff quality ---\n'
git diff --check
DIFF_RC=$?

printf '\n--- Config ownership ---\n'
if grep -Rni \
    'config/ros2_mcp.toml' \
    src/ros2_mcp \
    --include='*.py' \
    --exclude-dir='__pycache__'
then
    CONFIG_RC=1
else
    echo "No hard-coded config/ros2_mcp.toml references."
    CONFIG_RC=0
fi

printf '\n--- Results ---\n'
echo "Syntax:           $SYNTAX_RC"
echo "Pytest:           $PYTEST_RC"
echo "Collection:       $COLLECT_RC"
echo "Diff check:       $DIFF_RC"
echo "Config ownership: $CONFIG_RC"

if \
    [ "$SYNTAX_RC" -eq 0 ] && \
    [ "$PYTEST_RC" -eq 0 ] && \
    [ "$COLLECT_RC" -eq 0 ] && \
    [ "$DIFF_RC" -eq 0 ] && \
    [ "$CONFIG_RC" -eq 0 ]
then
    echo
    echo "PHASE 8 FINAL QUALITY CHECK: PASS"
else
    echo
    echo "PHASE 8 FINAL QUALITY CHECK: FAILED"
fi
```

Expected regression result:

```text
20 passed
```

Expected test collection:

```text
20 tests collected
```

Expected configuration ownership result:

```text
No hard-coded config/ros2_mcp.toml references.
```

---

# 79. Phase 8 Completion Criteria

Phase 8 is ready for completion when all of the following are true:

```text
[PASS] packaged default configuration exists
[PASS] centralized configuration resolution works
[PASS] explicit configuration works
[PASS] environment override works
[PASS] invalid explicit configuration is rejected
[PASS] safety uses centralized configuration
[PASS] wheel contains default configuration
[PASS] installed package runs outside repository
[PASS] installed CLI works
[PASS] installed MCP stdio works
[PASS] rclpy works in installed environment
[PASS] Codex can use installed MCP server
[PASS] 46 MCP tools are exposed
[PASS] representative MCP tools execute
[PASS] process verification uses dry-run
[PASS] permanent configuration tests exist
[PASS] permanent server lifespan test exists
[PASS] 20 tests pass
[PASS] syntax validation passes
[PASS] git diff quality check passes
```

---

# 80. Phase 8 Result

Phase 8 establishes that `ros2_mcp` is no longer only a source-tree development server.

It is verified as an installable ROS 2-aware MCP package with:

```text
robust configuration resolution
packaged defaults
isolated wheel installation
installed CLI
real MCP stdio operation
Codex compatibility
centralized safety configuration
permanent configuration tests
permanent server lifespan testing
```

Final verified regression result:

```text
20 passed
```

Installed MCP tool inventory:

```text
46 tools
```

The installed-package Codex verification completed with:

```text
all requested operations succeeded
no real ROS process started
no project file modified
```

---

# 81. Next Step

After completing this document:

```text
1. update the main README.md
2. run the final Phase 8 pre-commit quality check
3. inspect the complete Phase 8 diff
4. stage the Phase 8 files
5. run the staged quality check
6. commit Phase 8
7. push main to origin
```

After Phase 8, the generic `ros2_mcp` runtime has a stable foundation for future specialized MCP servers and integrations such as:

```text
ros2_control_mcp
MoveIt 2 integration
Nav2 integration
```

These specialized domains should remain separated from the generic ROS 2 MCP runtime.
