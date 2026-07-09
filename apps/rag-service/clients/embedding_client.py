import requests

EMBEDDING_SERVICE = "http://embedding-service:8002/embed"


def get_embedding(text: str):
    response = requests.post(EMBEDDING_SERVICE, json={"text": text}, timeout=10)

    response.raise_for_status()

    return response.json()["embedding"]
