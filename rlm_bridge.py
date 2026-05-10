import sys
import json
import os
import logging
from rlm import RLM
from rlm.logger import RLMLogger
from rich.console import Console
from rich.logging import RichHandler

# Use rich console for stderr feedback
console = Console(stderr=True)

# Configure logging to use RichHandler on stderr with DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("rlm_bridge")
logger.setLevel(logging.DEBUG)

def save_state(project_id, state_data):
    """Saves the distilled reasoning state to disk."""
    path = f"knowledge_base/states/{project_id}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state_data, f, indent=2)
    logger.info(f"💾 State saved for [bold green]{project_id}[/]")

def load_state(project_id):
    """Loads the previous reasoning state."""
    path = f"knowledge_base/states/{project_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def run_rlm(prompt, model_name, base_url, environment="local", project_id=None):
    """
    Connects to a local Ollama server and runs RLM completion with persistence.
    """
    try:
        logger.info(f"🚀 Initializing RLM [bold cyan]{model_name}[/] | Project: {project_id}")
        
        # Load previous knowledge if project_id is provided
        previous_knowledge = load_state(project_id) if project_id else {}
        
        # Build an enhanced prompt that includes previous reasoning
        enhanced_prompt = prompt
        if previous_knowledge:
            logger.info("📚 Loading existing knowledge into context...")
            enhanced_prompt = f"Previous Knowledge about this project: {json.dumps(previous_knowledge)}\n\nUser Query: {prompt}"

        rlm = RLM(
            backend="openai",
            backend_kwargs={
                "model_name": model_name,
                "base_url": base_url,
                "api_key": "ollama",
                "stream": True
            },
            environment=environment,
            verbose=True,
            logger=RLMLogger(log_dir="trajectories")
        )

        logger.info("🧠 [bold green]Starting recursive reasoning...[/]")
        result = rlm.completion(enhanced_prompt)

        # Post-process to extract new "Knowledge/Facts" for persistence
        if project_id:
            # We task a sub-LLM to distill the new reasoning into long-term facts
            logger.info("🧪 Distilling new reasoning into long-term knowledge...")
            distill_prompt = f"Distill the following reasoning into a set of permanent project facts (JSON format):\n{result.response}"
            distill_res = rlm.completion(distill_prompt) # recursive distillation
            try:
                new_facts = json.loads(distill_res.response)
                previous_knowledge.update(new_facts)
                save_state(project_id, previous_knowledge)
            except:
                logger.warning("⚠️ Failed to parse distilled facts as JSON, saving raw response.")
                previous_knowledge["latest_update"] = result.response
                save_state(project_id, previous_knowledge)

        logger.info("✅ [bold blue]Completion finished![/]")
        return {
            "status": "success",
            "response": result.response,
            "trajectory_log": getattr(result, "log_file", None)
        }
    except Exception as e:
        logger.error(f"❌ [bold red]RLM Error:[/] {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    try:
        # Read input from stdin
        logger.info("Bridge waiting for input...")
        input_raw = sys.stdin.read()
            
        if not input_raw:
            logger.error("No input received on stdin")
            sys.exit(1)
            
        logger.info(f"Received input length: {len(input_raw)}")
        input_data = json.loads(input_raw)
        
        prompt = input_data.get("prompt")
        model_name = input_data.get("model_name", "deepseek-r1:7b")
        base_url = input_data.get("base_url", "http://localhost:11434/v1")
        env = input_data.get("environment", "local")
        project_id = input_data.get("project_id") # New parameter for persistence

        if not prompt:
            print(json.dumps({"status": "error", "message": "No prompt provided"}))
            sys.exit(1)

        result = run_rlm(prompt, model_name, base_url, env, project_id)
        print(json.dumps(result))

    except Exception as e:
        logger.error(f"Bridge critical error: {str(e)}")
        print(json.dumps({"status": "error", "message": f"Bridge critical error: {str(e)}"}))
        sys.exit(1)
