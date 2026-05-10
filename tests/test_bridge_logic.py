import os
import json
import pytest
from rlm_bridge import save_state, load_state

# We use a test project ID
TEST_PROJECT = "tdd_unit_test"
STATE_FILE = f"knowledge_base/states/{TEST_PROJECT}.json"

def test_save_state_path_normalization():
    """
    EXPECTATION: When saving state, absolute paths matching the current 
    working directory should be converted to relative paths.
    """
    current_dir = os.getcwd()
    test_data = {
        "project_root": current_dir,
        "source_files": [
            os.path.join(current_dir, "src/main.rs"),
            "/absolute/path/outside/project" # This should stay absolute
        ],
        "nested": {
            "path": current_dir
        }
    }

    # Save state
    save_state(TEST_PROJECT, test_data)

    # Verify the file exists
    assert os.path.exists(STATE_FILE)

    # Read the raw file to check for normalization
    with open(STATE_FILE, "r") as f:
        saved_raw = f.read()
        saved_json = json.loads(saved_raw)

    # EXPECTATION: The absolute project root should NOT be in the file
    assert current_dir not in saved_raw, "Absolute path was not normalized in the JSON file!"
    
    # Check for relative markers
    assert "./src/main.rs" in saved_raw or "src/main.rs" in saved_raw
    assert "/absolute/path/outside/project" in saved_raw # Should remain untouched

def test_load_state_path_denormalization():
    """
    EXPECTATION: When loading state, relative paths should be expanded 
    back to absolute paths for the current machine.
    """
    current_dir = os.getcwd()
    relative_path = "src/main.rs"
    
    # Manually create a state file with a relative path
    test_data = {
        "file": relative_path
    }
    
    # We use a separate ID for this test
    LOAD_PROJECT = "tdd_load_test"
    path = f"knowledge_base/states/{LOAD_PROJECT}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(test_data, f)

    # Load the state using our new logic
    loaded_state = load_state(LOAD_PROJECT)

    # EXPECTATION: The relative path should have been expanded to absolute
    expected_abs = os.path.join(current_dir, relative_path)
    assert loaded_state["file"] == expected_abs
    print(f"[TDD] SUCCESS: Relative path was expanded to {expected_abs}")

if __name__ == "__main__":
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    test_save_state_path_normalization()
    test_load_state_path_denormalization()
    print("\n--- ALL LOGIC TESTS PASSED ---")
