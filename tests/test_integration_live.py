import subprocess
import json
import os
import pytest

# Paths
BRIDGE_SCRIPT = "rlm_bridge.py"
GRAILS_REPO_PATH = "/Users/walterduquedeestrada/IdeaProjects/grails-core/"

def run_bridge(payload):
    """Helper to run the bridge script as the Rust orchestrator would."""
    process = subprocess.Popen(
        ["uv", "run", "python", BRIDGE_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=json.dumps(payload))
    return json.loads(stdout), stderr

@pytest.mark.live
def test_full_stack_grails_analysis():
    """
    EXPECTATION: The bridge connects to Ollama, runs RLM, 
    and returns a successful architectural analysis of Grails.
    """
    if not os.path.exists(GRAILS_REPO_PATH):
        pytest.skip("Grails repo not found locally")

    payload = {
        "prompt": f"Scan the root of {GRAILS_REPO_PATH} and tell me if it is a Gradle or Maven project.",
        "model_name": "deepseek-r1:7b",
        "base_url": "http://localhost:11434/v1"
    }

    print("\n[Live Test] Sending request to RLM...")
    result, stderr = run_bridge(payload)

    # Expectations
    assert result["status"] == "success", f"Bridge failed: {result.get('message')} | Stderr: {stderr}"
    assert "response" in result
    
    response_text = result["response"].lower()
    
    # Logic-based Expectations
    assert "gradle" in response_text, "Expected RLM to identify Grails as a Gradle project."
    assert len(response_text) > 50, "Expected a substantial analysis, but got a very short response."
    
    print(f"[Live Test] SUCCESS: RLM identified the project type correctly.")

@pytest.mark.live
def test_hierarchy_discovery():
    """
    EXPECTATION: RLM must recursively navigate the Grails source to find 
    the implementation of a specific interface.
    """
    if not os.path.exists(GRAILS_REPO_PATH):
        pytest.skip("Grails repo not found locally")

    # We ask for something that requires looking at multiple files
    payload = {
        "prompt": f"In the repository {GRAILS_REPO_PATH}, find the 'GrailsApplication' interface "
                  f"and tell me the name of its primary default implementation class.",
        "model_name": "deepseek-r1:7b",
        "base_url": "http://localhost:11434/v1"
    }

    print("\n[Live Test] Starting Hierarchy Discovery (Deep Reasoning)...")
    result, _ = run_bridge(payload)

    assert result["status"] == "success"
    response = result["response"]
    
    # Specific Expectations:
    # 1. It must find the interface name
    assert "GrailsApplication" in response
    # 2. It must find the implementation (usually DefaultGrailsApplication)
    assert "DefaultGrailsApplication" in response
    
    print("[Live Test] SUCCESS: RLM successfully traced the class hierarchy.")

@pytest.mark.live
def test_ollama_connectivity():
    """
    EXPECTATION: The bridge can reach the Ollama API.
    """
    payload = {
        "prompt": "respond with the word 'READY'",
        "model_name": "deepseek-r1:7b",
        "base_url": "http://localhost:11434/v1"
    }
    
    result, _ = run_bridge(payload)
    assert result["status"] == "success", "Failed to connect to local Ollama server."
    assert "ready" in result["response"].lower()
