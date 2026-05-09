import sys
import json
import os
from rlm import RLM

def run_rlm(prompt, model_name, base_url, environment="local"):
    """
    Connects to a local vLLM (or OpenAI-compatible) server and runs RLM completion.
    """
    try:
        # Initialize RLM with the local vLLM server
        rlm = RLM(
            backend="openai", # vLLM is OpenAI-compatible
            backend_kwargs={
                "model_name": model_name,
                "base_url": base_url,
                "api_key": os.getenv("OPENAI_API_KEY", "cm-no-key-needed")
            },
            environment=environment
        )

        # Run completion
        result = rlm.completion(prompt)

        return {
            "status": "success",
            "response": result.response,
            "trajectory_log": getattr(result, "log_file", None) # Some versions of RLM might store this
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    # Expecting JSON input from stdin
    try:
        input_data = json.load(sys.stdin)
        
        prompt = input_data.get("prompt")
        model_name = input_data.get("model_name", "llama3") # Default model name
        base_url = input_data.get("base_url", "http://localhost:8000/v1")
        env = input_data.get("environment", "local")

        if not prompt:
            print(json.dumps({"status": "error", "message": "No prompt provided"}))
            sys.exit(1)

        result = run_rlm(prompt, model_name, base_url, env)
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Bridge error: {str(e)}"}))
        sys.exit(1)
