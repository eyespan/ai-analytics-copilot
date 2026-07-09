import requests
from config import OLLAMA_URL, OLLAMA_MODEL


def generate(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": 2048},
        },
        timeout=120,
    )

    if response.status_code != 200:
        print("OLLAMA ERROR:", response.text)

    response.raise_for_status()
    return response.json()["response"]
