# rlm-mcp: The Recursive Project Brain

`rlm-mcp` is an advanced Model Context Protocol (MCP) server that transforms your local repository into a **"Shared Project Brain."** It uses recursive reasoning (via [RLM](https://github.com/alexzhang13/rlm)) and local LLMs (Ollama) to analyze, reason, and remember your project's architecture, helping teams maintain deep understanding of complex codebases like Grails Core.

## Features
- **Frictionless Auto-Pilot:** Automatically installs Ollama, manages Python environments (`uv`), and pulls optimized reasoning models.
- **Persistent Knowledge:** Distills recursive reasoning into portable YAML knowledge bases that can be checked into Git.
- **Workspace-Aware:** Automatically discovers project configurations in `.mcp/` or `.rlm/` folders.
- **Recursive Reasoning:** Uses multi-step LLM loops to trace complex class hierarchies and architectural patterns.

## Quick Start
1. Ensure you have [Ollama](https://ollama.com/) installed and running.
2. Clone the repository and run:
   ```bash
   cargo run
   ```
3. The server will automatically:
    - Detect your OS and hardware.
    - Provision a hermetic Python environment using `uv`.
    - Pull the recommended `deepseek-r1:7b` model.
    - Launch the MCP server on stdio.

## Project Structure
- `.mcp/`: Configuration and project-specific knowledge base.
- `knowledge_base/`: Distilled "permanent facts" about your project (version-controlled).
- `trajectories/`: Raw logs of every "thinking" session (ignored by Git).

## Documentation & Roadmap
See [PLAN.md](./PLAN.md) for the full "Project Brain" architecture roadmap.

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
