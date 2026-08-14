# Embedding Service

## Purpose

`apps/embedding-service` is a small FastAPI service that converts text into vector embeddings.

It is used by the indexer when creating searchable repository documents.

## Source

```text
apps/embedding-service/
├── main.py
├── embeddings.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Model

Both `main.py` and `embeddings.py` load:

```text
sentence-transformers
model: all-MiniLM-L6-v2
```

The model is loaded once at module initialisation.

## HTTP API

### `GET /health`

Returns:

```json
{"status":"ok"}
```

### `GET /`

Returns:

```json
{"message":"Embedding Service Running"}
```

### `POST /embed`

Request model:

```python
class EmbeddingRequest(BaseModel):
    text: str
```

Example:

```json
{
  "text": "tensorflow deep learning Python"
}
```

The endpoint executes:

```python
model.encode(request.text).tolist()
```

and returns:

```json
{
  "embedding": [...]
}
```

## Python Helper

`embeddings.py` provides:

```python
def embed_text(text: str):
    return model.encode(text).tolist()
```

This is a direct Python helper separate from the FastAPI endpoint.

## Runtime Flow

```text
Repository Record
      |
      v
Indexer
      |
      v
POST /embed
      |
      v
SentenceTransformer
      |
      v
Vector
      |
      v
OpenSearch
```

## Consumer

The current indexer calls:

```text
http://embedding-service:80/embed
```

and expects the JSON field:

```text
embedding
```

## Startup Characteristics

Because the transformer model is loaded during module import, application startup includes model initialisation.

This means pod startup time and memory requirements are influenced by the embedding model.

## Failure Modes

Potential runtime failures include:

- model loading failure
- invalid input
- insufficient CPU/memory
- service connectivity failure from the indexer

The indexer performs retry logic for calls to `/embed`.

## Design Boundary

The embedding service does not perform:

- LLM generation
- model-provider routing
- BM25 search
- OpenSearch querying
- repository ingestion
- agent execution

Its responsibility is embedding generation.

## Level 7

The service remains independent of the selected answer-generation provider.

Choosing:

```text
Ollama
```

or:

```text
AWS Bedrock
```

for the LLM does not change the embedding service.

This separation allows retrieval embeddings and answer-generation models to evolve independently.
