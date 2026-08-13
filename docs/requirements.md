# ros2_mcp Requirements

This document describes the requirements for:

1. Developing and extending `ros2_mcp`
2. Starting and using the `ros2_mcp` MCP server

The Python package dependencies themselves are managed through `pyproject.toml` and `uv.lock`.

---

# 1. Requirements for Developing `ros2_mcp`

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

The current implementation targets ROS 2 Jazzy.

ROS-specific functionality must remain isolated behind the ROS adapter architecture so that support for future ROS 2 distributions can be added without redesigning the MCP and application layers.

---

## 1.2 Project Location

The development repository is expected at:

```text
~/projects/robotics/ros2_mcp
```

Before development, testing, or running project-local commands, enter the project directory and activate the Python environment.

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

Verify the basic environment with:

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

If the environment does not exist, create it with:

```bash
cd ~/projects/robotics/ros2_mcp

uv venv --python 3.12
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

uv sync
```

For an existing development environment:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

uv sync
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

A normal Jazzy installation should resolve `rclpy` from the ROS installation under:

```text
/opt/ros/jazzy/
```

The project must not vendor or duplicate `rclpy`.

---

## 1.6 Development Architecture

New functionality must follow the existing architecture:

```text
MCP Client
    |
    v
MCP Tool Layer
    |
    v
Application / Runtime Service
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

MCP-facing tools belong under:

```text
src/ros2_mcp/mcp/
```

---

## 1.7 Configuration Requirements

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

If no explicit configuration is provided, the packaged default configuration is used.

This allows an installed `ros2_mcp` package to run independently of the source repository.

---

## 1.8 Safety Requirements

New write-capable ROS operations must integrate with the existing safety model.

The safety layer is implemented under:

```text
src/ros2_mcp/ros/jazzy/safety.py
```

Important principles include:

- no arbitrary shell execution
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

## 1.9 Subprocess Requirements

Where external ROS commands are required, structured subprocess execution must be used.

Do not introduce:

```python
shell=True
```

Arguments must be passed as structured argument lists.

Example concept:

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

## 1.10 ROS Executor Requirements

ROS executor access must remain serialized through the shared adapter executor helpers.

ROS modules must not independently perform uncontrolled concurrent executor spins.

This protects the shared `rclpy` executor from concurrent MCP requests.

Any new functionality requiring executor spinning must use the existing executor synchronization mechanism in `JazzyRosAdapter`.

---

## 1.11 QoS Requirements

Topic operations must support ROS 2 QoS correctly.

For general topic reads, automatic QoS selection should remain the preferred default where applicable.

The current QoS implementation is located in:

```text
src/ros2_mcp/ros/jazzy/qos.py
src/ros2_mcp/ros/jazzy/qos_auto.py
```

New topic functionality should reuse these components rather than implementing independent QoS logic.

---

## 1.12 Testing Requirements

Every meaningful extension should include appropriate tests.

The current test structure is:

```text
tests/
├── integration/
└── unit/
```

Unit tests should verify application and configuration behavior.

Integration tests should verify behavior that crosses architectural boundaries such as:

```text
MCP
  ->
Application
  ->
ROS Adapter
```

The server lifespan integration test verifies that the complete MCP server can initialize, expose its tools, execute representative operations, and shut down correctly.

---

## 1.13 Development Test Commands

Before committing changes, run:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
pytest --collect-only -q
git diff --check
```

The current Version 1 baseline is:

```text
20 tests
46 MCP tools
```

A change must not unintentionally reduce these baselines.

---

## 1.14 MCP Tool Inventory Verification

The MCP server tool inventory can be checked directly through the MCP Python client:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import asyncio

from mcp import Client
from ros2_mcp.server import create_server


async def main() -> None:
    """Verify the MCP tool inventory."""
    server = create_server()

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.list_tools()

        names = sorted(
            tool.name
            for tool in result.tools
        )

        print("Tool count:", len(names))

        for name in names:
            print(name)


asyncio.run(main())
PY
```

The Version 1 baseline is:

```text
46 MCP tools
```

---

## 1.15 Git Requirements

Before committing:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git status
git diff --check
pytest -q
```

The working tree should only contain intentional changes.

After committing:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

git status
git log -3 --oneline --decorate
```

---

# 2. Requirements for Starting `ros2_mcp`

There are two supported usage scenarios:

1. Start from the development repository
2. Start the installed `ros2-mcp` package

The installed-package approach is preferred for normal MCP client usage because it does not depend on the source repository working directory.

---

## 2.1 Start from the Development Repository

Enter the project and initialize both environments:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Recommended ROS runtime variables:

```bash
export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

Start the MCP server with:

```bash
ros2-mcp
```

Alternatively, during development:

```bash
python -m ros2_mcp.server
```

The server uses MCP over:

```text
stdio
```

Therefore, when started by an MCP client, stdin and stdout belong to the MCP transport.

---

## 2.2 Complete Development Start Command

For manual development startup:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp
```

---

## 2.3 Start as an Installed Package

An installed package exposes the console command:

```text
ros2-mcp
```

ROS 2 still needs to be sourced before the server starts.

Example:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp
```

The installed package contains its own default configuration:

```text
ros2_mcp/config/default.toml
```

It therefore does not require:

```text
~/projects/robotics/ros2_mcp/config/ros2_mcp.toml
```

or the source repository as its working directory.

---

## 2.4 ROS Environment Required by MCP Clients

An MCP client starting `ros2-mcp` must provide the ROS environment.

At minimum:

```text
ROS_DISTRO=jazzy
AMENT_PREFIX_PATH=/opt/ros/jazzy
ROS_DOMAIN_ID=30
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

The safest method is to source ROS before executing the server:

```bash
bash -lc 'source /opt/ros/jazzy/setup.bash && exec ros2-mcp'
```

If a dedicated virtual environment contains the installed executable, use its absolute path:

```bash
bash -lc 'source /opt/ros/jazzy/setup.bash && exec /path/to/venv/bin/ros2-mcp'
```

---

## 2.5 Codex MCP Registration

For Codex, the MCP server should be registered as a stdio server.

Conceptually:

```text
Codex
   |
   | MCP / stdio
   v
ros2-mcp
   |
   | rclpy
   v
ROS 2 Jazzy
```

The server process must start inside a valid ROS 2 environment.

For development, the command can start the project environment and ROS environment before executing the server.

For an installed deployment, prefer the installed `ros2-mcp` executable instead of depending on the source repository.

---

## 2.6 Verify ROS Before Starting MCP

Before debugging MCP connectivity, verify ROS itself:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

echo "ROS_DISTRO=$ROS_DISTRO"
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"

python - <<'PY'
import rclpy

print("rclpy:")
print(rclpy.__file__)
PY
```

If `rclpy` cannot be imported, fix the ROS environment before debugging MCP.

---

## 2.7 Verify the MCP Server

A complete MCP lifespan verification can be performed with the existing integration test:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q tests/integration/test_server_lifespan.py
```

The test verifies representative server functionality including:

- server initialization
- MCP tool registration
- runtime health
- safety guardrails
- controlled process dry-run
- clean server shutdown

---

## 2.8 Full Startup Verification

Before using the server with an external MCP client:

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

python -m compileall -q src tests
pytest -q
```

Expected Version 1 baseline:

```text
20 passed
```

---

## 2.9 Current Version 1 Baseline

The completed `ros2_mcp` Version 1 release provides:

```text
ROS distribution: ROS 2 Jazzy
Python:           3.12
MCP transport:    stdio
MCP tools:        46
Tests:            20
Configuration:    packaged TOML + optional override
Safety:           enabled
Packaging:        installable Python package
CLI:              ros2-mcp
```

The package has been verified both:

```text
from the development repository
```

and:

```text
as an installed package outside the repository
```

---

# 3. Quick Reference

## Development

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

uv sync

python -m compileall -q src tests
pytest -q
git diff --check
```

## Start the Development Server

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2-mcp
```

## Test the Complete MCP Server

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

pytest -q tests/integration/test_server_lifespan.py
```

## Full Regression Test

```bash
cd ~/projects/robotics/ros2_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python -m compileall -q src tests
pytest -q
pytest --collect-only -q
git diff --check
```

---

# 4. Development Rule

`ros2_mcp` is the generic ROS 2 runtime MCP server.

Generic ROS 2 runtime functionality belongs here.

Specialized domain functionality should remain in separate MCP servers where appropriate.

Examples:

```text
ros2_mcp
    Generic ROS 2 runtime operations

ros2_control_mcp
    ros2_control-specific operations

moveit2_mcp
    MoveIt 2-specific operations

nav2_mcp
    Nav2-specific operations
```

This separation keeps the generic ROS 2 MCP layer stable while allowing specialized robotics MCP servers to evolve independently.
