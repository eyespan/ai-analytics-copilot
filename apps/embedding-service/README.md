# Embedding Service

## Purpose
The Embedding Service generates vector representations used by the retrieval/indexing architecture.

```text
Text -> Embedding Service -> Vector -> OpenSearch
```

## Responsibilities
- Accept text for embedding.
- Run the configured embedding model.
- Return vector representations.
- Support the indexing pipeline.

It does not own repository ingestion, search ranking, LLM routing or agent execution.

## Indexing Flow
```text
ClickHouse -> Indexer
                  |
                  v
          Embedding Service
                  |
                  v
              Embedding
                  |
                  v
             OpenSearch
```

## Model
The project uses a sentence-transformers-based embedding approach. The exact model and vector dimension are deployment configuration and must remain compatible with the OpenSearch mapping.

## Data Contract
Conceptually:
```json
{"text":"text to embed"}
```
returns an embedding vector. The exact HTTP schema should follow the deployed implementation.

## Operations
Embedding generation can be CPU/memory intensive. Production considerations include model warm-up, concurrency, batching, caching and scaling.

## Failure Handling
The indexer should distinguish successful embedding generation from failed generation before indexing a record.

## Testing
Validate:
1. Known text produces an embedding.
2. Vector dimensionality is correct.
3. The vector can be indexed.
4. Vector retrieval can find the record.

## Level 6 / Level 7
Embedding generation is independent from the selected LLM provider.

## Design Principle
Embedding inference for search is a separate responsibility from LLM generation for answers.
