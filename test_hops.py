import requests
import time

SYSTEM_PROMPT = "You are a recursive reasoning agent. Follow the user instructions exactly."

# Simulate a growing history
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Start a chain of thought. Step 1: say 'thinking'"},
    {"role": "assistant", "content": "thinking"},
    {"role": "user", "content": "Step 2: say 'reasoning'"},
    {"role": "assistant", "content": "reasoning"},
    {"role": "user", "content": "Step 3: say 'FINAL'"}
]

def test_hop(msg_slice, hop_name):
    print(f"--- Testing {hop_name} ---")
    payload = {
        "model": "deepseek-r1:7b",
        "messages": msg_slice,
        "stream": False
    }
    start = time.time()
    try:
        response = requests.post("http://127.0.0.1:11434/v1/chat/completions", json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()['choices'][0]['message']['content'][:50]}...")
        print(f"Time: {time.time() - start:.2f}s")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Hop 1: Just system + 1st user
test_hop(messages[:2], "Hop 1")
# Hop 2: Full history up to 2nd user
test_hop(messages[:4], "Hop 2")
# Hop 3: Full history up to 3rd user
test_hop(messages, "Hop 3")
