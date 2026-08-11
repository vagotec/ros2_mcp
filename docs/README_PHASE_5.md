# Phase 5 - Project Adapter

## Goal

Add safe ROS 2 project creation capabilities without breaking the established modular architecture.

Phase 5 introduces a separate Project Adapter path next to the ROS runtime path.

## Architecture

```text
MCP Client
    |
    v
Project MCP Tools
    |
    v
ProjectService
    |
    v
ProjectAdapter
    |
    v
FilesystemProjectAdapter
    |
    v
SafeFilesystem
    |
    v
Configured Allowed Root
```

The Project Adapter is independent from the ROS Runtime Adapter.

## Security Boundary

All project filesystem operations are restricted to:

```text
/home/sarvg/projects/robotics/ros2_mcp
```

The configured root is stored in:

```text
config/ros2_mcp.toml
```

Current configuration:

```toml
[project]
allowed_root = "/home/sarvg/projects/robotics/ros2_mcp"
```

Project tools cannot access paths outside this root.

## SafeFilesystem

`SafeFilesystem` is responsible for validating project paths.

It protects against:

```text
../ path traversal
absolute paths outside the allowed root
symlink escapes
```

Paths are resolved before access is granted.

## ProjectAdapter

The ProjectAdapter defines the project operations required by the application layer.

Current interface:

```text
create_workspace
create_package
create_node
create_launch_file
create_parameter_file
create_tests
```

The application layer does not depend directly on filesystem implementation details.

## FilesystemProjectAdapter

The filesystem implementation creates ROS 2 project files inside the configured security boundary.

It does not execute external commands.

Phase 5 therefore does not call:

```text
ros2 pkg create
colcon build
colcon test
```

Command execution belongs to Phase 6.

## create_workspace

Creates a basic ROS 2 workspace:

```text
workspace/
└── src/
```

Example:

```text
demo_ws/
└── src/
```

## create_package

Creates a minimal ROS 2 Python package using `ament_python`.

Example:

```text
demo_ws/
└── src/
    └── demo_pkg/
        ├── demo_pkg/
        │   └── __init__.py
        ├── resource/
        │   └── demo_pkg
        ├── package.xml
        └── setup.py
```

The generated package includes:

```text
ament_python
ament_pytest
setuptools
```

The generated `setup.py` supports installation of:

```text
launch/*.launch.py
config/*.yaml
```

## create_node

Creates a Python ROS 2 node inside an existing package.

Example:

```text
demo_pkg/
└── demo_pkg/
    └── demo_node.py
```

The generated node includes:

```text
rclpy.init()
Node subclass
rclpy.spin()
node.destroy_node()
rclpy.shutdown()
```

Generated Python code is syntax checked by the test suite.

## create_launch_file

Creates a Python ROS 2 launch file.

Example:

```text
demo_pkg/
└── launch/
    └── demo.launch.py
```

The generated launch file uses:

```text
LaunchDescription
launch_ros.actions.Node
```

The package setup installs launch files into the package share directory.

## create_parameter_file

Creates a ROS 2 YAML parameter file.

Example:

```text
demo_pkg/
└── config/
    └── demo_params.yaml
```

Generated structure:

```yaml
demo_node:
  ros__parameters: {}
```

The package setup installs YAML files into the package share directory.

## create_tests

Creates a basic pytest file.

Example:

```text
demo_pkg/
└── test/
    └── test_package_import.py
```

The generated test verifies that the generated Python package can be imported.

## ProjectService

The ProjectService exposes project use cases independently from filesystem implementation details.

It delegates all operations through the ProjectAdapter.

The application layer does not directly use:

```text
Path
mkdir
write_text
SafeFilesystem
```

## MCP Project Tools

The MCP server currently exposes:

```text
create_workspace
create_package
create_node
create_launch_file
create_parameter_file
create_tests
```

These tools are write operations.

They are annotated as:

```text
read_only_hint=False
destructive_hint=False
idempotent_hint=True
open_world_hint=False
```

## Runtime and Project Separation

The server now contains two independent application paths.

Runtime path:

```text
MCP
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
```

Project path:

```text
MCP
 |
 v
ProjectService
 |
 v
ProjectAdapter
 |
 v
FilesystemProjectAdapter
 |
 v
SafeFilesystem
```

This separation prevents project file generation logic from leaking into ROS runtime logic.

## Server Lifecycle

The MCP application context now contains:

```text
Settings
JazzyRosAdapter
RuntimeService
ProjectService
```

The ProjectService is initialized using:

```text
SafeFilesystem
    |
    v
FilesystemProjectAdapter
    |
    v
ProjectService
```

## Tests

Current test result:

```text
27 passed
```

Tests cover:

```text
SafeFilesystem path resolution
parent traversal rejection
absolute path rejection
symlink escape rejection

workspace creation
package creation
node generation
launch generation
parameter YAML generation
pytest generation

ProjectService delegation

MCP project tool discovery
MCP project creation workflow
MCP filesystem boundary enforcement

generated Python syntax
temporary workspace cleanup
```

## MCP Integration Workflow

The MCP integration test currently performs:

```text
create_workspace
    |
    v
create_package
    |
    v
create_node
    |
    v
create_launch_file
    |
    v
create_parameter_file
    |
    v
create_tests
```

The generated temporary workspace is removed after the test.

## Current MCP Runtime Tools

Read-only runtime tools:

```text
list_nodes
list_topics
topic_info
list_services
read_topic
```

## Current MCP Project Tools

Project creation tools:

```text
create_workspace
create_package
create_node
create_launch_file
create_parameter_file
create_tests
```

## Files Added

Phase 5 adds:

```text
src/ros2_mcp/project/adapter.py
src/ros2_mcp/project/filesystem/adapter.py
src/ros2_mcp/project/filesystem/safe_filesystem.py
src/ros2_mcp/application/project/service.py
src/ros2_mcp/mcp/project_tools.py

tests/unit/test_safe_filesystem.py
tests/unit/test_project_adapter.py
tests/unit/test_project_service.py
tests/integration/test_mcp_project_tool.py
```

## Files Modified

Phase 5 modifies:

```text
config/ros2_mcp.toml
src/ros2_mcp/config/settings.py
src/ros2_mcp/server.py
```

## Architecture Decisions

Phase 5 establishes these rules:

* Project operations are separated from ROS runtime operations.
* Filesystem access goes through SafeFilesystem.
* Allowed roots are configuration values.
* MCP does not directly access the filesystem.
* Application services depend only on adapters.
* Project generation does not execute shell commands.
* Generated ROS files follow normal ROS 2 package conventions.
* External build and test execution belongs to Phase 6.
* Generated code contains short English documentation.
* Write operations remain restricted to the configured project root.

## Known Limitations

Phase 5 currently supports only Python ROS 2 packages.

It does not yet support:

```text
ament_cmake packages
C++ nodes
URDF packages
ros2_control packages
build execution
test execution
dependency resolution
automatic package dependency updates
```

These can be added in later phases without changing the core architecture.

## Phase Status

```text
Phase 5 - Project Adapter

COMPLETED
```

## Next Phase

Phase 6 introduces controlled project execution.

Planned functionality:

```text
build_project
run_tests
```

Phase 6 will need to handle:

```text
subprocess execution
working directory restrictions
timeouts
captured stdout
captured stderr
exit codes
command allowlists
```

All command execution must remain inside the configured allowed project root.

