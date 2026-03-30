import requests
from config.settings import OLLAMA_URL, MODEL_NAME
import json
import re

def clean_llm_output(raw: str) -> str:
    """
    Removes ```json ... ``` formatting
    """
    # Remove ```json and ```
    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)

    return raw.strip()


def call_ollama(prompt: str) -> str:
    """
    Sends prompt to Ollama and returns raw text response
    """

    url = f"{OLLAMA_URL}/api/generate"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        # print(f"Data received is: {data}")
        stripped = data.get("response", "").strip()
        cleaned = clean_llm_output(stripped)
        print(f"Data stripped: {cleaned}")
        return cleaned
    except Exception as e:
        print("❌ Ollama Error:", e)

def call_ollama_json(prompt: str) -> dict:
    raw = call_ollama(prompt)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON:", raw)
        return {}