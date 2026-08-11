# ROS 2 MCP

A modular MCP server for connecting MCP clients such as Codex to ROS 2.

## Goals

The project provides two clearly separated capabilities:

* Runtime access to a running ROS 2 system
* Safe creation and modification of ROS 2 projects

The architecture keeps MCP, application logic, ROS integration, and project management separated.

## Architecture

```text
MCP Client
    |
    v
MCP Layer
    |
    v
Application Layer
   / \
  v   v
ROS   Project
Adapter Adapter
  |      |
  v      v
rclpy   Safe Filesystem
  |
  v
ROS 2 / DDS
```

## Project Principles

* Modular architecture
* MCP and ROS 2 remain separated
* ROS access goes through a dedicated adapter
* ROS distributions should remain replaceable
* MCP should remain as stateless as possible
* MCP clients should remain replaceable
* Runtime access starts read-only
* Write operations require explicit safety mechanisms
* Project file access is restricted to approved project roots
* No unnecessary frameworks
* Docker and Kubernetes are planned for later phases

## Development Phases

1. Foundation
2. ROS Adapter
3. ROS Discovery
4. Topic Reading
5. Project Adapter
6. Build and Test
7. Extended Runtime
8. Controlled Write and Deployment Readiness

Detailed documentation for each phase is stored in `docs/README_PHASE_X.md`.

## Current Status

Phase 2 completed. Phase 3 is next.

## Development Environment

* Ubuntu 24.04
* ROS 2 Jazzy
* Python 3.12
* uv
* MCP Python SDK
* pytest

## Repository

This repository is developed independently and is intended to be published later as its own GitHub repository.
