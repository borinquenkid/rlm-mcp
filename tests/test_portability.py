import json
import os
import subprocess
import pytest

BRIDGE_SCRIPT = "rlm_bridge.py"
PROJECT_ID = "test_portability_proj"
STATE_FILE = f"knowledge_base/states/{PROJECT_ID}.json"

def run_bridge(payload):
    process = subprocess.Popen(
        ["uv", "run", "python", BRIDGE_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=json.dumps(payload))
    try:
        return json.loads(stdout), stderr
    except:
        return {"status": "error", "message": stdout}, stderr

def test_path_portability_expectation():
    """
    RED TEST: Verifies that absolute paths are converted to relative paths in the saved state.
    """
    # Cleanup previous state
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

    abs_path = os.getcwd()
    payload = {
        "prompt": f"This is a test. Store a fact that the project root is exactly {abs_path}",
        "project_id": PROJECT_ID,
        "model_name": "llama3.2:3b", # Fast model for TDD
        "base_url": "http://localhost:11434/v1"
    }

    print(f"\n[TDD] Running bridge with absolute path: {abs_path}")
    result, stderr = run_bridge(payload)

    assert result["status"] == "success", f"Bridge failed: {stderr}"
    assert os.path.exists(STATE_FILE), "Knowledge base state file was not created."

    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    
    state_str = json.dumps(state)
    
    # EXPECTATION: The absolute path should NOT be in the saved JSON.
    # It should have been converted to '.' or a relative string.
    assert abs_path not in state_str, f"Absolute path '{abs_path}' found in saved state! It should be relative."
    print("[TDD] SUCCESS: Absolute path was normalized (or test passed because logic is already there).")

if __name__ == "__main__":
    pytest.main([__file__, "-s"])
