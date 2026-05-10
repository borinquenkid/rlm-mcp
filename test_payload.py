import requests
import json
import time

SYSTEM_PROMPT = "You are a helpful assistant."

payload = {
    "model": "llama3.2:3b",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "say HI"}
    ],
    "stream": False
}

print("Sending SMALL system prompt to Ollama...")
start = time.time()
try:
    response = requests.post(
        "http://127.0.0.1:11434/v1/chat/completions",
        json=payload,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()['choices'][0]['message']['content']}")
    else:
        print(f"Error Response: {response.text}")
    print(f"Time taken: {time.time() - start:.2f}s")
except Exception as e:
    print(f"Error: {e}")
    print(f"Time until error: {time.time() - start:.2f}s")
