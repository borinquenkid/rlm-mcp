# Spec: Memory-Efficient Graph Traversal (The "Indexing" Strategy)

## Objective
To enable `rlm-mcp` to reason over massive codebases without loading the entire project knowledge base into the LLM's context window. This system implements "Lazy-Load Reasoning" where the RLM retrieves specific nodes and edges on demand.

## Technical Components
1. **Knowledge Index:** A simplified SQLite or JSON structure that maps symbols (classes, functions, interfaces) to their location, implementation, and relationship metadata.
2. **MCP Tools:**
   - `graph_search(query: str)`: Fuzzy search for symbols in the index.
   - `graph_query(symbol: str)`: Fetch detailed metadata (parent, children, file_path) for a specific node.
3. **Reasoning Orchestration:** The RLM is instructed to *never* assume the structure of the codebase. It must query the index for every cross-file navigation.

## API / Interface Design
- **Index Entry Shape:**
  ```json
  {
    "symbol": "GrailsApplication",
    "type": "interface",
    "file": "./src/main/java/org/grails/GrailsApplication.java",
    "parents": [],
    "children": ["DefaultGrailsApplication"]
  }
  ```
- **Tool Logic:** The Rust `RlmHandler` will intercept these tool calls and translate them into efficient lookups in the knowledge base, returning small, targeted payloads to the Python sandbox.

## Implementation Roadmap
- [ ] Task 4.1: Define `IndexSchema` (Rust Struct + SQL Table definition).
- [ ] Task 4.2: Implement `graph_search` and `graph_query` as native MCP tools.
- [ ] Task 4.3: Update RLM Bridge prompt instructions to enforce index-first reasoning.

## Success Criteria
- Reasoning speed is constant regardless of project size (O(1) lookups).
- System memory usage stays below 8GB (including model + OS).
- The RLM successfully traces hierarchies via tool calls, not just by hallucinating from its context window.
