import os

# =====================
# OpenSearch
# =====================

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")

INDEX_NAME = "github-repos"

TOP_K = 20


# =====================
# Embeddings
# =====================

EMBEDDING_SERVICE = os.getenv(
    "EMBEDDING_SERVICE", "http://embedding-service:8002/embed"
)


# =====================
# Ollama
# =====================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


# =====================
# RAG
# =====================

MAX_CONTEXT_DOCS = 3

RETRIEVAL_METHOD = "hybrid"
