import os
import requests


class RagClient:

    def __init__(self):

        self.base_url = os.getenv(
            "RAG_SERVICE_URL",
            "http://rag-service:8001"
        )

    # ----------------------------------
    # Level 4 Retrieval Debug Endpoint
    # ----------------------------------
    def debug_retrieval(self, query: str):

        response = requests.post(
            f"{self.base_url}/debug-retrieval",
            json={
                "query": query
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()

    # ----------------------------------
    # Level 4 Cross Encoder Reranker
    # ----------------------------------
    def rerank(self, query: str, docs: list):

        response = requests.post(
            f"{self.base_url}/rerank",
            json={
                "query": query,
                "documents": docs
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()["results"]

    # ----------------------------------
    # Future Level 5+
    # ----------------------------------
    def ask(self, query: str):

        response = requests.post(
            f"{self.base_url}/ask",
            json={
                "query": query
            }
        )

        response.raise_for_status()

        return response.json()