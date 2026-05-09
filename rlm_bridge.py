import sys
import json
import os
import logging
from rlm import RLM

# Configure logging to stderr so it doesn't interfere with JSON stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s: %(message)s')
logger = logging.getLogger("rlm_bridge")

def run_rlm(prompt, model_name, base_url, environment="local"):
    """
    Connects to a local Ollama (or OpenAI-compatible) server and runs RLM completion.
    """
    try:
        logger.info(f"Initializing RLM with model={model_name}, url={base_url}")
        
        # Initialize RLM
        rlm = RLM(
            backend="openai", # Ollama is OpenAI-compatible
            backend_kwargs={
                "model_name": model_name,
                "base_url": base_url,
                "api_key": "ollama" # Dummy key for Ollama
            },
            environment=environment
        )

        logger.info("Starting RLM completion...")
        result = rlm.completion(prompt)

        return {
            "status": "success",
            "response": result.response,
            "trajectory_log": getattr(result, "log_file", None)
        }
    except Exception as e:
        logger.error(f"RLM Error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    try:
        # Read input from stdin
        input_raw = sys.stdin.read()
        if not input_raw:
            logger.error("No input received on stdin")
            sys.exit(1)
            
        input_data = json.loads(input_raw)
        
        prompt = input_data.get("prompt")
        model_name = input_data.get("model_name", "deepseek-r1:7b")
        base_url = input_data.get("base_url", "http://localhost:11434/v1")
        env = input_data.get("environment", "local")

        if not prompt:
            print(json.dumps({"status": "error", "message": "No prompt provided"}))
            sys.exit(1)

        result = run_rlm(prompt, model_name, base_url, env)
        print(json.dumps(result))

    except Exception as e:
        logger.error(f"Bridge critical error: {str(e)}")
        print(json.dumps({"status": "error", "message": f"Bridge critical error: {str(e)}"}))
        sys.exit(1)
