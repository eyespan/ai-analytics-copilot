# Indexer Service

## Purpose
The Indexer Service prepares repository data for search.

```text
ClickHouse -> Indexer -> Embedding Service -> OpenSearch
```

## Responsibilities
- Read repository records from ClickHouse.
- Prepare searchable records.
- Obtain embeddings.
- Write searchable/vector representations to OpenSearch.

It does not own agent orchestration, model routing, tool policy or evaluation.

## Data Flow
```text
ClickHouse
    |
    v
Indexer
    |
    +--> Embedding Service
    |
    v
OpenSearch
```

## ClickHouse
ClickHouse is the repository data store/source in the project's architecture.

## Embeddings
Embedding generation is separated into its own service, keeping indexing and model inference responsibilities independent.

## OpenSearch
OpenSearch stores the searchable representation consumed by RAG, including repository metadata and vector/search fields according to the deployed mapping.

## Operational Testing
Validate:
1. ClickHouse contains source records.
2. Indexing succeeds.
3. OpenSearch contains indexed records.
4. RAG can retrieve them.

## Observability
Indexing should make record counts, failures, embedding errors, OpenSearch errors and latency diagnosable.

## Level 6 / Level 7
The indexing pipeline is independent of LLM provider choice.

## Design Principle
Separate data preparation from request-time AI inference.
