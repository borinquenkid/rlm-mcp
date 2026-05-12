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

### Phase 7: Sub-MCP Integration (Core)
- [ ] **Task 7.1: Hybrid Server/Client Orchestration**
    - Update `src/main.rs` to maintain active `Client` connections to Sub-MCPs.
    - Implement tool-routing to map `repowise:*` (or other sub-MCP) requests to the child MCP.
- [ ] **Task 7.2: Discovery & Injection**
    - Automatically fetch tools from context providers like **Repowise** and inject into RLM bridge.
    - *Note: Repowise is highly recommended over basic codebase-memory tools due to its token efficiency, Git intelligence, and ADR tracking, making it the ideal "data provider" for RLM's reasoning engine.*
- [ ] **Task 7.3: Proxy & Distill**
    - Proxy graph/context queries and distill the results using the lightweight reasoning engine.

## Technical Debt & Considerations
- **Memory Pressure:** The current model footprint (7B) is tuned for 16GB total RAM machines.
- **Port Conflict Handling:** Basic scanning is in place, but deeper multi-server port orchestration is needed for Phase 4.

## Open Questions for Contributors
- **Inception Security:** How strictly should we isolate the Sub-MCPs?
- **Tool Naming:** How should we resolve collisions if two Sub-MCPs share tool names?
