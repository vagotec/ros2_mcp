# Phase 14 – Remote MCP / Streamable HTTP

## 1. Goal

Phase 14 extends `ros2_mcp` from a local stdio-only MCP server to a server that can also be accessed remotely through MCP Streamable HTTP.

The implementation follows the MCP `2026-07-28` protocol baseline and MCP Python SDK `2.0.0`.

The goal of this phase is to provide a clean remote transport without changing the existing ROS 2 runtime architecture or introducing client-specific behavior.

Phase 14 adds:

- MCP Streamable HTTP transport
- a dedicated HTTP server entry point
- configurable HTTP host, port, and MCP path
- DNS rebinding protection
- allowed Host validation
- allowed Origin validation
- optional Bearer token authentication
- OAuth Protected Resource Metadata
- authenticated remote MCP access
- real HTTP integration tests
- LAN access validation

The existing stdio transport remains available and unchanged.

---

## 2. Architecture

The runtime architecture remains transport-independent.

    MCP Client
        |
        +-------------------+
        |                   |
        v                   v
      stdio          Streamable HTTP
        |                   |
        +---------+---------+
                  |
                  v
              MCPServer
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
        rclpy / ROS 2 Jazzy

The HTTP transport does not bypass the existing application or ROS adapter layers.

No ROS-specific logic is implemented in the HTTP layer.

---

## 3. Transport Separation

The original executable remains:

    ros2-mcp

It starts the MCP server using the standard stdio transport.

Phase 14 adds:

    ros2-mcp-http

The HTTP executable starts the same MCP server through Streamable HTTP.

The two entry points therefore expose the same MCP capabilities through different transports.

    ros2-mcp
        |
        +--> stdio

    ros2-mcp-http
        |
        +--> Streamable HTTP

This keeps transport selection outside the ROS runtime implementation.

---

## 4. MCP Protocol Baseline

Phase 14 continues to target:

    MCP protocol:
    2026-07-28

    MCP Python SDK:
    2.0.0

The existing protocol regression baseline remains unchanged.

Real Streamable HTTP client tests verified protocol negotiation using:

    MCP-Protocol-Version: 2026-07-28

The HTTP transport therefore preserves the MCP protocol baseline established in earlier phases.

---

## 5. HTTP Server

The HTTP server is implemented in:

    src/ros2_mcp/http_server.py

It creates a Starlette ASGI application from the existing MCP server.

The MCP Python SDK provides the Streamable HTTP transport implementation.

The application is served using Uvicorn.

The HTTP layer is intentionally small.

Its responsibilities are limited to:

    configuration
    transport setup
    transport security
    optional authentication
    ASGI server startup

ROS 2 runtime functionality remains outside this module.

---

## 6. HTTP Configuration

HTTP configuration is part of the normal `ros2_mcp` configuration system.

The default configuration contains an `[http]` section.

The important settings are:

    host
    port
    path
    enable_dns_rebinding_protection
    allowed_hosts
    allowed_origins

Default local endpoint:

    http://127.0.0.1:8000/mcp

The default host intentionally binds to loopback instead of exposing the server to the network automatically.

Remote exposure must therefore be an explicit configuration decision.

---

## 7. Backward-Compatible Configuration

Older `ros2_mcp` configuration files may not contain an `[http]` section.

Phase 14 preserves compatibility with these configurations.

When the HTTP section is absent, safe defaults are derived:

    host:
    127.0.0.1

    port:
    8000

    path:
    /mcp

This prevents the HTTP feature from breaking existing stdio configurations.

Existing users are not required to add HTTP configuration unless they want to use the HTTP transport.

---

## 8. Streamable HTTP

Phase 14 uses MCP Streamable HTTP rather than introducing a custom REST API.

The MCP endpoint therefore remains a real MCP protocol endpoint.

The transport supports the existing MCP capabilities:

    Tools
    Prompts
    Resources
    Resource Templates
    Server Instructions
    protocol discovery
    structured arguments
    structured results
    MCP errors

No ROS 2 operation is exposed through an independent HTTP REST interface.

This is intentional.

The protocol boundary remains MCP.

---

## 9. Current MCP Inventory

The verified MCP inventory remains:

    MCP Tools:
    46

    MCP Prompts:
    6

    Static MCP Resources:
    0

    MCP Resource Templates:
    9

Phase 14 does not add ROS 2 runtime functionality.

It adds another transport for the existing MCP API.

---

## 10. Real HTTP MCP Validation

The Streamable HTTP server was tested with a real MCP client.

Verified operations include:

    protocol discovery
    Tool discovery
    Prompt discovery
    Resource Template discovery
    Tool invocation
    Resource reading
    Prompt retrieval

A real HTTP invocation of:

    get_runtime_health

successfully reached the ROS 2 runtime through the complete architecture.

The HTTP transport therefore does not merely start an ASGI application.

It has been tested end-to-end through MCP.

---

## 11. ROS 2 Runtime Validation

The HTTP transport was tested against the real ROS 2 Jazzy runtime.

A remote MCP Tool invocation returned a structured runtime health result containing:

    health
    graph
    diagnostics
    rosout

This verifies the complete path:

    MCP HTTP Client
            |
            v
    Streamable HTTP
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
    JazzyRosAdapter
            |
            v
      ROS 2 Jazzy

---

## 12. LAN Validation

Remote access was also tested through the machine's LAN interface.

Verified LAN endpoint:

    http://192.168.2.182:8000/mcp

The MCP client successfully performed:

    protocol negotiation
    Tool discovery
    Prompt discovery
    Resource Template discovery
    Tool invocation

This confirms that the HTTP transport is not limited to loopback operation.

The LAN address is environment-specific and is not part of the packaged default configuration.

---

## 13. Explicit Remote Exposure

Remote exposure is deliberately opt-in.

The packaged default remains:

    127.0.0.1

A LAN or other remote deployment must explicitly configure another bind address.

Conceptually:

    host = LAN address
    port = configured MCP port
    path = /mcp

This prevents an installation from unexpectedly exposing ROS 2 runtime control to the network.

---

## 14. DNS Rebinding Protection

Phase 14 enables the MCP SDK transport security mechanism.

The configuration supports:

    enable_dns_rebinding_protection
    allowed_hosts
    allowed_origins

DNS rebinding protection is enabled by default.

This is particularly important because an MCP server may expose state-changing ROS 2 runtime operations.

---

## 15. Host Validation

When DNS rebinding protection is enabled, incoming Host headers are validated.

Tests verified that an invalid Host header is rejected.

Observed rejection:

    HTTP 421
    Invalid Host header

This behavior is provided by the MCP transport security implementation.

Allowed hosts are explicitly configurable.

---

## 16. Origin Validation

Incoming Origin headers are also validated when transport security is enabled.

Tests verified that an invalid Origin is rejected.

Observed rejection:

    HTTP 403
    Invalid Origin header

Allowed origins are explicitly configurable.

This prevents arbitrary browser origins from being implicitly trusted.

---

## 17. Authentication Architecture

Phase 14 adds optional Bearer token authentication for controlled remote and lab access.

Authentication is implemented separately from ROS 2 runtime logic.

Conceptually:

    Remote MCP Client
           |
           | Authorization: Bearer ...
           v
    MCP Authentication
           |
           v
        MCPServer
           |
           v
    RuntimeService
           |
           v
         ROS 2

The ROS adapter does not know how authentication works.

This preserves the architectural boundary between transport/security and ROS runtime operations.

---

## 18. Static Bearer Token Verifier

The authentication helper is implemented in:

    src/ros2_mcp/mcp/auth.py

Phase 14 provides a small:

    StaticBearerTokenVerifier

for controlled local and laboratory deployments.

The verifier validates one configured Bearer token and returns an MCP `AccessToken` representation for authenticated requests.

This is intentionally not presented as a full identity platform.

It provides a simple authentication option while keeping the server compatible with the MCP SDK authentication architecture.

---

## 19. Authentication Environment

Authentication secrets are not stored in the packaged TOML configuration.

The HTTP server obtains authentication-sensitive values through environment configuration.

This keeps static credentials outside the repository and normal configuration file.

The server can therefore operate in two modes:

    HTTP without authentication

or:

    HTTP with Bearer authentication

depending on deployment configuration.

---

## 20. Unauthorized Requests

Authentication tests verify that requests without a valid token are rejected.

Observed response:

    HTTP 401 Unauthorized

The response includes a `WWW-Authenticate` Bearer challenge.

Requests with an invalid Bearer token are also rejected.

Only a valid configured token is allowed to reach the MCP server.

---

## 21. Authenticated MCP Client

A real authenticated Streamable HTTP MCP client was tested.

The authenticated client successfully performed:

    MCP initialization
    Tool discovery
    Prompt discovery
    Resource Template discovery
    Tool invocation

The real tool invocation:

    get_runtime_health

completed successfully.

This validates authentication across the actual MCP HTTP transport rather than only testing the token verifier in isolation.

---

## 22. OAuth Protected Resource Metadata

When authentication is enabled, the MCP SDK exposes OAuth Protected Resource Metadata for the MCP endpoint.

For an MCP path:

    /mcp

the metadata endpoint is:

    /.well-known/oauth-protected-resource/mcp

The endpoint was verified to return HTTP 200.

The returned metadata identifies:

    resource
    authorization_servers
    scopes_supported
    bearer_methods_supported

The generic path:

    /.well-known/oauth-protected-resource

is not exposed for this path-specific MCP resource and returned HTTP 404 during validation.

This behavior is consistent with the path-specific protected resource metadata generated for the MCP endpoint.

---

## 23. Authentication Scope

The Phase 14 remote access scope is:

    ros2_mcp:access

The scope represents general authenticated access to the current MCP server.

Fine-grained authorization per ROS operation is intentionally outside the Phase 14 scope.

Runtime safety continues to be enforced independently through the existing `ros2_mcp` safety layer.

---

## 24. Authentication and Runtime Safety

Authentication does not replace ROS runtime safety.

The security model is layered.

    Network binding
          |
          v
    Transport security
          |
          v
    Authentication
          |
          v
    MCP Tool annotations
          |
          v
    Runtime safety policy
          |
          v
      RosAdapter
          |
          v
        ROS 2

A successfully authenticated client is still subject to the existing runtime safety controls.

Protected ROS resources and configured runtime limits therefore remain effective.

---

## 25. No Arbitrary Remote Shell

Remote MCP access does not introduce arbitrary shell execution.

The existing project boundary remains unchanged.

The server does not expose:

    arbitrary shell commands
    arbitrary ROS CLI commands
    arbitrary filesystem operations

Remote clients can only invoke explicitly registered MCP capabilities.

This is particularly important once the MCP server is reachable over a network.

---

## 26. Existing stdio Compatibility

The original stdio server remains available through:

    ros2-mcp

Phase 14 does not replace stdio.

This allows the project to support both local process-based MCP clients and remote Streamable HTTP MCP clients without duplicating the ROS runtime implementation.

---

## 27. HTTP Entry Point

The package exposes:

    ros2-mcp-http

through the Python project scripts configuration.

The entry point starts the Streamable HTTP server using the configured:

    host
    port
    path

This provides a normal installed executable in the same way that `ros2-mcp` provides the stdio executable.

---

## 28. Packaging

The project package version remains:

    0.1.0

Phase 14 extends the functionality intended for the first public release.

The project now packages both executable entry points:

    ros2-mcp
    ros2-mcp-http

---

## 29. Integration Tests

Phase 14 adds dedicated Streamable HTTP integration tests.

The relevant test modules are:

    tests/integration/test_streamable_http.py
    tests/integration/test_streamable_http_auth.py

The tests cover both unauthenticated and authenticated HTTP operation.

---

## 30. Authentication Unit Tests

Authentication-specific unit tests are implemented in:

    tests/unit/test_auth.py

These tests verify the static Bearer token verifier independently from the HTTP integration tests.

This keeps authentication logic testable without requiring a running HTTP server.

---

## 31. Configuration Tests

The existing settings tests were extended for HTTP configuration.

The tests cover:

    packaged HTTP defaults
    legacy configuration compatibility
    invalid HTTP port handling
    transport security defaults
    derived security defaults

This protects both new HTTP behavior and compatibility with configurations created before Phase 14.

---

## 32. Transport Security Tests

Dedicated integration tests verify the MCP SDK transport security behavior.

Verified cases include:

    valid local MCP HTTP access
    invalid Origin rejection
    invalid Host rejection

Expected results:

    invalid Origin:
    HTTP 403

    invalid Host:
    HTTP 421

These are permanent regression tests rather than manual-only checks.

---

## 33. MCP Protocol Header Validation

Real Streamable HTTP traffic was inspected during Phase 14.

The client sent the negotiated MCP protocol version through HTTP requests.

Observed protocol:

    2026-07-28

The protocol header was present for operations including:

    server/discover
    tools/list
    prompts/list
    resources/templates/list
    tools/call
    resources/read
    prompts/get

This confirms that protocol negotiation remains visible across the HTTP transport.

---

## 34. Resource Validation

The Streamable HTTP client successfully accessed the existing Resource Template architecture.

A real resource read was performed through HTTP.

The resource layer therefore behaves consistently between local and remote MCP operation.

No HTTP-specific resource implementation was required.

---

## 35. Prompt Validation

The existing MCP Prompt architecture was also tested through Streamable HTTP.

The client successfully retrieved an MCP Prompt through the remote transport.

No prompt-specific HTTP implementation was introduced.

The same MCP server capability is reused across transports.

---

## 36. Tool Validation

The existing MCP Tool architecture was tested through Streamable HTTP.

The client successfully discovered the complete Tool inventory and invoked a real ROS 2 runtime Tool.

The Tool layer therefore remains transport-independent.

---

## 37. Server Instructions

Server Instructions remain configured on the same MCP server instance.

Phase 14 does not introduce transport-specific instructions.

The same server behavior is therefore available to stdio and HTTP clients according to the capabilities exposed by each MCP client implementation.

---

## 38. HTTP Dependencies

The Streamable HTTP implementation uses the HTTP/ASGI components provided by the MCP SDK stack together with Uvicorn.

The project does not introduce a custom web framework architecture around the MCP protocol.

The HTTP server remains an infrastructure adapter around the existing MCP server.

---

## 39. Security Boundary

Remote access changes the threat boundary of the application.

For this reason Phase 14 deliberately combines:

    loopback default binding
    explicit remote exposure
    Host validation
    Origin validation
    DNS rebinding protection
    optional Bearer authentication
    existing ROS safety policies
    no arbitrary shell
    no arbitrary ROS CLI

No single mechanism is treated as sufficient by itself.

---

## 40. Deployment Boundary

Phase 14 provides the application-level building blocks for remote MCP access.

It does not attempt to implement a complete Internet-facing production platform.

Production concerns such as:

    TLS termination
    certificate lifecycle
    reverse proxy configuration
    enterprise identity provider integration
    centralized secrets management
    rate limiting
    network policy
    production observability

belong to the deployment environment.

The application remains suitable for controlled local, LAN, container, and future orchestrated deployments.

---

## 41. TLS

The application does not implement custom TLS handling inside the ROS MCP architecture.

For production deployments, TLS should normally be terminated by deployment infrastructure such as a reverse proxy, ingress controller, service mesh, or equivalent platform component.

This keeps transport encryption infrastructure separate from ROS runtime logic.

---

## 42. Future Authentication Evolution

The Phase 14 static Bearer token mechanism is intentionally small.

The MCP SDK already exposes authentication abstractions such as:

    TokenVerifier
    AuthSettings
    OAuth authorization server integration

A future deployment can therefore replace the static verifier with a stronger identity integration without changing ROS runtime functionality.

The current implementation provides the architectural seam required for that evolution.

---

## 43. No Client-Specific Workaround

Phase 14 does not contain special server behavior for Codex, Claude, or another individual MCP client.

The server implements MCP protocol capabilities.

Clients are expected to interact with those capabilities according to the MCP protocol.

This preserves client portability.

---

## 44. ROS Distribution Isolation

The HTTP implementation does not depend directly on `rclpy`.

ROS 2 Jazzy-specific behavior remains isolated in:

    src/ros2_mcp/ros/jazzy/

The transport therefore does not weaken the distribution-adapter architecture established in earlier phases.

---

## 45. Action Lifecycle Support

The existing managed ROS 2 Action lifecycle remains available through remote MCP access.

The runtime supports:

    start_action_goal
    get_action_status
    cancel_action_goal

Managed Action state includes:

    goal state
    completion state
    result
    feedback

Action feedback is therefore available through the managed Action status model.

A separate feedback-specific MCP Tool is not required for the current release.

---

## 46. Runtime Feature Boundary

Phase 14 does not add subsystem-specific MCP servers.

The generic `ros2_mcp` project remains focused on the ROS 2 runtime ecosystem.

Subsystem-specific integrations such as:

    ros2_control
    Nav2
    MoveIt 2

remain outside this generic runtime server.

ROS 1 compatibility is also outside the project scope.

---

## 47. Regression Status

After Phase 14 implementation and integration testing, the complete automated test suite reports:

    48 passed

The suite includes:

    unit tests
    ROS runtime tests
    MCP tests
    protocol tests
    Resource tests
    Prompt tests
    stdio tests
    Streamable HTTP tests
    transport security tests
    authentication tests

---

## 48. Phase 14 Files

Important Phase 14 implementation files:

    src/ros2_mcp/http_server.py
    src/ros2_mcp/mcp/auth.py
    src/ros2_mcp/config/settings.py
    src/ros2_mcp/config/default.toml
    src/ros2_mcp/server.py
    pyproject.toml

Important Phase 14 test files:

    tests/integration/test_streamable_http.py
    tests/integration/test_streamable_http_auth.py
    tests/unit/test_auth.py
    tests/unit/test_server.py
    tests/unit/test_settings.py

---

## 49. Final Architecture

After Phase 14:

    MCP Clients
         |
         +--------------------+
         |                    |
         v                    v
       stdio           Streamable HTTP
         |                    |
         |            Transport Security
         |                    |
         |             Authentication
         |                    |
         +---------+----------+
                   |
                   v
               MCPServer
                   |
          +--------+--------+
          |        |        |
          v        v        v
        Tools    Prompts  Resources
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
       ROS 2 Jazzy

The architecture remains modular across:

    client
    transport
    authentication
    MCP protocol
    application runtime
    ROS abstraction
    ROS distribution implementation

---

## 50. Phase 14 Final Status

Verified development state:

    Branch:
    dev

    Package version:
    0.1.0

    ROS distribution:
    Jazzy

    Operating system target:
    Ubuntu 24.04

    Python:
    3.12

    MCP protocol:
    2026-07-28

    MCP SDK:
    2.0.0

    MCP Tools:
    46

    MCP Prompts:
    6

    Static MCP Resources:
    0

    MCP Resource Templates:
    9

    stdio transport:
    PASS

    Streamable HTTP:
    PASS

    Real HTTP MCP client:
    PASS

    LAN MCP access:
    PASS

    DNS rebinding protection:
    PASS

    Host validation:
    PASS

    Origin validation:
    PASS

    Bearer authentication:
    PASS

    Unauthenticated request rejection:
    PASS

    Invalid token rejection:
    PASS

    Authenticated MCP Tool invocation:
    PASS

    OAuth Protected Resource Metadata:
    PASS

    ROS 2 runtime access through HTTP:
    PASS

    Complete automated test suite:
    48 passed

---

## Phase 14 Result

    PHASE 14 REMOTE MCP / STREAMABLE HTTP: PASS

Phase 14 adds standards-based remote MCP access to `ros2_mcp` while preserving the existing stdio transport, ROS adapter architecture, runtime safety model, MCP capability inventory, and MCP `2026-07-28` protocol baseline.

The project now supports both local and remote MCP clients without duplicating ROS 2 runtime functionality.

Remote exposure remains explicit, transport security is enabled by default, optional Bearer authentication is available for controlled deployments, and authenticated access is integrated through the MCP SDK authentication architecture.

With Phase 14 complete, the next project stage is the `v0.1.0` release freeze and promotion of the validated `dev` branch to `main`.
