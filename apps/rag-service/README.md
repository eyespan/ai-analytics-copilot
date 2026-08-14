# RAG Service

## Purpose

`apps/rag-service` is the retrieval and RAG application used by the orchestrator.

It combines repository retrieval techniques developed across the earlier project levels.

## Source Structure

```text
apps/rag-service/
├── main.py
├── clickhouse_client.py
├── config.py
├── retrieval/
│   ├── bm25.py
│   ├── hybrid.py
│   ├── vector.py
│   └── reranker.py
├── llm/
├── evaluation/
├── Dockerfile
├── requirements.txt
└── README.md
```

## API

### `GET /health`

Returns:

```json
{"status":"ok"}
```

### `GET /`

Returns:

```json
{"message":"RAG Service Running"}
```

### `GET /db-test`

Tests ClickHouse connectivity and returns the ClickHouse version.

### `GET /top-repos`

Reads top repository information from ClickHouse and returns formatted results.

### `POST /vector-search`

Request:

```json
{"query":"machine learning"}
```

Calls the vector retrieval implementation.

### `POST /search`

Request:

```json
{"query":"machine learning"}
```

Calls:

```text
hybrid_search(query)
```

### `POST /ask`

Performs:

```text
hybrid retrieval
      |
      v
answer generation
```

and returns the query, retrieval information, answer and sources.

### `POST /debug-retrieval`

Exposes the internal retrieval stages:

```text
query
  |
  v
query expansion
  |
  +--> BM25
  |
  +--> vector
  |
  v
RRF fusion
```

### `POST /debug-rerank`

Runs:

```text
BM25
+
Vector
  |
RRF
  |
Reranker
```

and returns the reranked results.

### `POST /eval-retrieval`

Evaluates a query against an expected repository using:

```text
recall_at_k
reciprocal_rank
```

### `POST /eval-batch-retrieval`

Runs the batch retrieval evaluation.

### `POST /eval-reranker-ab`

Compares baseline fused retrieval with reranked retrieval and reports metrics and rank changes.

## Retrieval Architecture

The current code imports:

```text
retrieval.bm25
retrieval.vector
retrieval.hybrid
retrieval.reranker
```

The architecture is:

```text
Query
  |
  v
Query Expansion
  |
  +----------------+
  |                |
  v                v
 BM25            Vector
  |                |
  +-------+--------+
          |
          v
      RRF Fusion
          |
          v
       Reranker
          |
          v
    Relevant Documents
```

## ClickHouse

The RAG service contains a ClickHouse client abstraction:

```text
clickhouse_client.py
```

ClickHouse is used for repository/event data and connectivity testing.

The supplied Level 7 architecture also keeps ClickHouse as part of the Kubernetes data layer.

## OpenSearch

The retrieval implementation uses OpenSearch-backed search/index data through the retrieval modules.

The index used by the indexing service is:

```text
github-repos
```

## Embeddings

Vector retrieval is separated from embedding generation. The indexer calls the independent embedding service when preparing OpenSearch documents.

## Reranking

The Level 4 reranking path uses:

```text
retrieval/reranker.py
```

The debug endpoint labels the method as:

```text
cross-encoder
```

and supports top-k reranked results.

## Orchestrator Integration

The orchestrator uses a `RagClient` to call the RAG service.

The orchestrator pipeline calls the RAG debug retrieval path and then performs reranking through its RAG client.

This means retrieval is kept outside the main orchestrator process.

## Evaluation

Retrieval evaluation is separate from the Level 6/7 agent evaluation.

RAG evaluation includes:

```text
recall@k
reciprocal rank
batch evaluation
reranker A/B comparison
```

## Design Boundary

RAG service owns:

- retrieval
- fusion
- reranking
- retrieval evaluation
- repository data access

It does not own:

- model-provider routing
- agent planning
- tool permissions
- final orchestration workflow
- Level 6 agent trace replay

## Level 7

Level 7 changes the deployment environment rather than redesigning the retrieval algorithms.

The service can therefore continue using the same retrieval pipeline while being deployed in Kubernetes.
