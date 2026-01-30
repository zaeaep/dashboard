import os
import json
import requests
import argparse
from dotenv import load_dotenv

#https://openwebui.uni-freiburg.de/?model=standard-reasoning-ufr
#https://openwebui.uni-freiburg.de/?model=openai%2Fgpt-5.2-llmlb
#https://openwebui.uni-freiburg.de/?model=openai%2Fgpt-5.1-codex-max-llmlb
# -------------------------------------------------
# 1️⃣ Load the API key from a .env file (or from env vars)
# -------------------------------------------------
load_dotenv()                                   # reads .env in the cwd
API_KEY = os.getenv("OPEN_WEB_UI_API_KEY")     # <-- put your token here

if not API_KEY:
    raise ValueError(
        "API key not found. Set OPEN_WEB_UI_API_KEY in your environment."
    )

# -------------------------------------------------
# 2️⃣ Define the request
# -------------------------------------------------

BASE_URL = "https://openwebui.uni-freiburg.de"
CHAT_ENDPOINT = "/api/v1/chat/completions"
url = f"{BASE_URL}{CHAT_ENDPOINT}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    # Optional but handy for debugging:
    "Accept": "application/json",
    }
def chat_completion(message="Why is the sky blue?"):
    payload = {
        "model": "openai/gpt-5.2-llmlb",  # "standard-reasoning-ufr", "gpt-oss-120b-llmlb"
        "messages": [
            {"role": "user", "content": message}
        ]
        # You can also tweak temperature, max_tokens, etc.
        # "temperature": 0.7,
        # "max_tokens": 512,
    }

    # -------------------------------------------------
    # 3️⃣ Send the request
    # -------------------------------------------------
    response = requests.post(url, headers=headers, json=payload, timeout=60)

    # -------------------------------------------------
    # 4️⃣ Handle the response
    # -------------------------------------------------
    if response.status_code == 200:
        data = response.json()
        # The OpenAI‑compatible format puts the answer in `choices[0].message.content`
        answer = data["choices"][0]["message"]["content"]
        print("🤖 Model answer:\n", answer)
    else:
        # Print a helpful debug dump
        print(f"❌ HTTP {response.status_code}")
        try:
            print("Response JSON:", response.json())
        except json.JSONDecodeError:
            print("Raw response:", response.text)

def list_models():
    url = f"{BASE_URL}/api/v1/models"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

#print("Available models:", json.dumps(list_models(), indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat completion using Open Web UI API")
    parser.add_argument("message", nargs="?", default="Why is the sky blue?",
                        help="The message to send to the model")
    args = parser.parse_args()
    
    chat_completion(args.message)