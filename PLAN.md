# Implementation Plan: rlm-mcp (Frictionless & Generic)

## Overview
`rlm-mcp` is a zero-config MCP server designed to be hardware-aware. It handles the automated installation and management of Ollama and the Python RLM environment, ensuring optimal performance on both Apple Silicon (Unified Memory) and x86_64 (Dedicated GPU/CPU) architectures.

## Architecture Decisions
- **Orchestrator (Rust):** Lifecycle manager for all subsystems.
- **Inference (Ollama):** High-performance, pre-compiled engine.
- **Library (rlm):** Managed via `uv` in a hermetic `.venv`.
- **Memory Strategy (The "8GB Rule"):** To account for IDE and OS overhead (assuming a 16GB total RAM machine), we target a **~5GB - 8GB model footprint**. This prevents "swapping" and ensures the machine remains responsive for coding.
- **Target Model:** `deepseek-r1:7b` (High reasoning, fits comfortably in 8GB at Q4/Q5 quantization).

## Task List

### Phase 0: The Universal Orchestrator
- [ ] **Task 0.1: Platform & Memory Detection**
    - Detect OS (Mac, Linux, Windows).
    - Detect Architecture (Apple Silicon vs x86_64).
    - Check for existing `ollama` and `uv`.
- [ ] **Task 0.2: Automated Ollama Setup**
    - **Install:** If missing, download and install Ollama (Mac: CLI/App, Linux: curl script, Windows: installer).
    - **Start:** If port 11434 is closed, run `ollama serve` in the background.
    - **Model:** Run `ollama pull deepseek-r1:7b`.
- [ ] **Task 0.3: Python Auto-Pilot**
    - Ensure `uv` is available.
    - Run `uv sync` to install `rlms` into a project-local `.venv`.

### Phase 1: The RLM Bridge
- [ ] **Task 1.1: Bridge Script (`rlm_bridge.py`)**
    - Interface logic for `rlm` communicating with the local Ollama API (`/v1`).

### Phase 2: MCP Integration
- [ ] **Task 2.1: Rust MCP Server**
    - Implement `rlm_completion` tool.
    - Implement `system_status` tool (reports GPU/CPU/Memory health).

## Hardware Optimization
| Architecture | Acceleration | Model Quantization |
| :--- | :--- | :--- |
| **Apple Silicon (M1-M4)** | Metal (Unified) | Q5_K_M or Q6_K (~5-6GB) |
| **x86_64 + NVIDIA** | CUDA (Dedicated) | AWQ/GPTQ (~5GB) |
| **x86_64 (CPU Only)** | AVX2/AVX512 | Q4_0 (Low latency) |

## Verification
- **Zero-to-Hero Test:** Delete `.venv` and Ollama, then run `cargo run`. The system should be "Ready" and serving completions within the time it takes to download the model (~4.5GB).
