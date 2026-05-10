# Project Brain: rlm-mcp Roadmap

`rlm-mcp` is an autonomous "Project Brain" that orchestrates recursive reasoning and multi-agent workflows.

## Current State: PRODUCTION READY
The system is a fully autonomous orchestrator.
- **Auto-pilot:** Zero-config setup (Ollama + Python + UV + Models).
- **Persistent Memory:** Distilled reasoning state is saved in YAML (Git-compatible).
- **Workspace-Aware:** Automatically loads local project knowledge bases.
- **Self-Healing:** Can update itself to the latest GitHub version.

---

## Roadmap

### Completed
- [x] **Core Orchestration:** System detection, Ollama/Python auto-setup, and bridge script.
- [x] **Reasoning Stack:** Persistent, relative-path YAML state storage (Apache-compliant).
- [x] **MCP Interface:** `rlm_completion` and `system_status` tools implemented.
- [x] **Distribution:** Multi-platform CI/CD via `cargo-dist` & GitHub Actions.
- [x] **Self-Maintenance:** `self_update` tool for autonomous maintenance.

### Future/Planned Enhancements
- [ ] **Task 4.1: Sub-MCP Client Logic (Inception)**
    - Implement a Rust client to connect to external MCP servers (stdio/SSE).
- [ ] **Task 4.2: Tool Proxying**
    - Dynamically inject Sub-MCP tool definitions into the Python RLM sandbox.
- [ ] **Task 4.3: Recursive Tool Delegation**
    - Allow RLM to call Sub-MCP tools and verify their outputs before finalizing answers.
- [ ] **Task 5.3: Sandbox Security (E2B/Docker)**
    - Add support for containerized code execution for safer RLM tool use.

## Technical Debt & Considerations
- **Memory Pressure:** The current model footprint (7B) is tuned for 16GB total RAM machines.
- **Port Conflict Handling:** Basic scanning is in place, but deeper multi-server port orchestration is needed for Phase 4.

## Open Questions for Contributors
- **Inception Security:** How strictly should we isolate the Sub-MCPs?
- **Tool Naming:** How should we resolve collisions if two Sub-MCPs share tool names?
