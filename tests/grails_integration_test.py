import sys
import os
import json
from rlm import RLM

# Add the project root to path so we can import rlm if needed, 
# though 'uv sync' should have installed it in the venv.

GRAILS_REPO_PATH = "/Users/walterduquedeestrada/IdeaProjects/grails-core/"

def test_grails_analysis():
    print(f"--- Starting Integration Test: Grails Core Analysis ---")
    print(f"Target Repo: {GRAILS_REPO_PATH}")

    # Initialize RLM pointing to our local Ollama instance
    rlm = RLM(
        backend="openai",
        backend_kwargs={
            "model_name": "deepseek-r1:7b",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama"
        },
        environment="local"
    )

    # The prompt tasks RLM with exploring the Grails core codebase.
    # Because RLM has a code-execution sandbox, it can run 'ls' and 'cat' 
    # (via python's os/open) to explore the repo recursively.
    prompt = f"""
    I want to understand the core architectural pattern of Grails 6.
    The repository is located at {GRAILS_REPO_PATH}.
    
    Please explore the directory structure, identify a key 'Core' component 
    (like the ApplicationContext or Plugin management), and summarize how 
    it initializes in the current 'main' branch.
    """

    print("Sending prompt to RLM (this involves recursive reasoning and may take a few minutes)...")
    try:
        result = rlm.completion(prompt)
        
        print("\n--- RLM Response ---")
        print(result.response)
        print("\n--- Test Summary ---")
        print(f"Recursive Calls: {getattr(result, 'calls', 'N/A')}")
        print(f"Trajectory Log Saved: {getattr(result, 'log_file', 'None')}")
        
        if result.response and len(result.response) > 100:
            print("SUCCESS: RLM provided a substantial architectural analysis.")
        else:
            print("FAILURE: RLM response was too brief or empty.")

    except Exception as e:
        print(f"CRITICAL ERROR during RLM execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not os.path.exists(GRAILS_REPO_PATH):
        print(f"Error: Grails repo not found at {GRAILS_REPO_PATH}")
        sys.exit(1)
    
    test_grails_analysis()
