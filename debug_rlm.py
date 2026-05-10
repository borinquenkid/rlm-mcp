from rlm import RLM
import os

print("Initializing RLM...")
rlm = RLM(
    backend="openai",
    backend_kwargs={
        "model_name": "deepseek-r1:7b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama"
    },
    environment="local"
)

print("Starting completion...")
# Use a prompt that definitely doesn't require recursion
result = rlm.completion("What is 1+1?")
print(f"Result: {result.response}")
