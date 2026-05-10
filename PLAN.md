# Implementation Plan: rlm-mcp (The "Project Brain" Edition)

## Overview
`rlm-mcp` is an advanced Model Context Protocol (MCP) server that provides recursive reasoning via the `rlm` library. It is designed to be checked into repositories as a "Shared Project Brain," enabling teams to share architectural insights and orchestrate multiple MCP servers through a single recursive reasoning loop.

## Architecture Decisions
- **Master Orchestrator:** `rlm-mcp` acts as both a server (to the IDE) and a client (to other "Sub-MCPs").
- **Path Portability:** All reasoning artifacts are stored using relative paths to ensure they are version-control friendly.
- **Tool Injection:** Capabilities from Sub-MCPs are injected as native Python functions into the RLM reasoning sandbox.
- **Workspace Awareness:** Automatically detects and loads project-specific configurations from a `.mcp/` or `.rlm/` root folder.

## Task List

### Phase 0-2: Foundation (Completed/Refining)
- [x] Hardware/OS Detection (Rust)
- [x] Automated Ollama & Python Setup
- [x] Basic RLM Bridge & MCP Server
- [ ] **Task 2.3: Path Normalization (Critical for Git)**
    - Update `rlm_bridge.py` to convert all absolute paths to relative paths before saving state.
    - **Acceptance:** Knowledge base JSON contains no machine-specific paths (e.g., uses `./src` instead of `/Users/name/proj/src`).

### Phase 3: Workspace & Team Integration
- [ ] **Task 3.1: Workspace Auto-Discovery**
    - Implement logic to find the nearest `.mcp/` or `.rlm/` folder in the file tree.
    - Load `knowledge_base/` and `rlm_config.json` from this location.
- [ ] **Task 3.2: Artifact Management (Git integration)**
    - Standardize the `.mcp/` structure:
        - `knowledge_base/`: Distilled project facts (CHECKED IN).
        - `trajectories/`: Raw reasoning logs (IGNORED).
        - `prompts/`: Project-specific reasoning instructions.
- [ ] **Task 3.3: `sync_codebase` Enhancements**
    - Implement file-hashing (SHA-256) to trigger re-reasoning only on changed files.

### Phase 4: MCP Inception (Recursive Tooling)
- [ ] **Task 4.1: Sub-MCP Client Logic (Rust)**
    - Implement a client in the Rust server that can connect to other standard MCP servers (stdio or SSE).
- [ ] **Task 4.2: Tool Proxying**
    - Dynamically map Sub-MCP tools to the Python RLM environment.
    - *Example:* A tool `git_get_diff` in a sub-MCP becomes `mcp.git.get_diff()` in RLM's Python REPL.
- [ ] **Task 4.3: Configuration-Driven Inception**
    - Read `rlm_config.json` and automatically boot/connect to all listed Sub-MCPs.

### Phase 5: Production Distribution
- [ ] **Task 5.1: Asset Embedding**
    - Embed `rlm_bridge.py` and `pyproject.toml` into the Rust binary.
- [ ] **Task 5.2: Release Automation**
    - GitHub Actions for cross-platform (Mac/Linux/Windows) binary builds.

## Port & Multi-Server Strategy
- `rlm-mcp` will manage its own internal port registry for sub-MCPs to prevent collisions between the master brain and its specialized workers.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular Dependencies | High | Prevent an MCP from loading itself as a sub-MCP. |
| Memory Pressure | Med | RLM will monitor total system memory and skip high-cost sub-tasks if IDE is active. |
| Path Drift | Med | Normalize paths at every save/load cycle in the bridge. |

## Open Questions
- **Sub-MCP Lifecycle:** Should `rlm-mcp` kill sub-MCPs when it exits, or leave them running for other clients?
- **Tool Naming:** How should we handle name collisions if two sub-MCPs have a tool with the same name? (e.g., `list_files`).
