# RAG Service

## Purpose
The RAG service retrieves relevant repository information for AI responses.

```text
Query
 +--> BM25
 +--> Vector
      |
      v
   Hybrid
      |
      v
  Reranking
      |
      v
 Relevant Context
```

## Retrieval
The observed runtime trace exposes `bm25`, `vector` and `hybrid` retrieval counts. Results can include repository name, description, language, retrieval score and rerank score.

## Data Architecture
ClickHouse is the project's repository data store/source. OpenSearch provides the search/indexing layer.

```text
Repository Data -> ClickHouse -> Indexer -> OpenSearch -> RAG
```

## Runtime Flow
```text
Orchestrator -> RAG -> BM25/Vector/Hybrid -> Reranking -> Context -> Orchestrator/LLM
```

## Observability
Retrieval operations appear in execution traces with event type `retrieval`, success state and latency.

## Failure Handling
A retrieval failure should be distinguishable from a successful search with zero matches and should be observable.

## Testing
An `/ask` request can be inspected for its `trace.retrieval` section.

## Level 6 / Level 7
Provider selection does not change retrieval. The same retrieved context can be supplied to Ollama or Bedrock.

## Design Principle
Keep knowledge retrieval separate from LLM execution.
