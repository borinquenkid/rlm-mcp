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

## Multi-Agent Configuration
`rlm-mcp` is designed to orchestrate multiple specialized AI tools. You can "inject" sub-MCP servers into the Master Brain by adding them to `.mcp/rlm_config.json`:

```json
{
  "sub_servers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "."]
    }
  }
}
```

Once defined, `rlm-mcp` will automatically discover these tools, making them available to your recursive reasoning engine (e.g., `mcp.git.get_diff()`).

## Usage with MCP Clients
To use `rlm-mcp` in your IDE (like Claude Desktop), add this to your MCP configuration:

```json
{
  "mcpServers": {
    "rlm-mcp": {
      "command": "/path/to/rlm-mcp"
    }
  }
}
```
`rlm-mcp` will then auto-provision the local Ollama backend and Python environment on its first launch.
