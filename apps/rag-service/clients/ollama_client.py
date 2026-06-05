import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()
    return response.json()["response"]