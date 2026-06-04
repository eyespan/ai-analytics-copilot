# AI Analytics Copilot — Level 1 (Keyword + Embedding Ingestion Pipeline)

## Overview

This is Level 1 of the AI Analytics Copilot system.

It implements a full data ingestion pipeline:

ClickHouse → Indexer Service → Embedding Service → OpenSearch

The system extracts GitHub repository data, generates embeddings, and indexes documents into OpenSearch for keyword-based search.

---

## 🧱 Architecture


```mermaid
flowchart TD
    CH[(ClickHouse DB\ngithub.github_events)]
    IDX[indexer-service\nPython pipeline]
    EMB[embedding-service\nFastAPI + SBERT]
    OS[(OpenSearch\ngithub-repos index)]

    CH --> IDX
    IDX --> EMB
    IDX --> OS
```



---

## ⚙️ Services

### 1. ClickHouse
- Stores GitHub repository metadata
- Source of truth for ingestion

### 2. Indexer Service
- Reads data from ClickHouse
- Calls embedding service
- Indexes documents into OpenSearch

### 3. Embedding Service
- FastAPI service
- Uses `sentence-transformers`
- Endpoint:


POST /embed


### 4. OpenSearch
- Stores documents + embeddings
- Used for keyword search (BM25)

---

## 🚀 How to Run

### 1. Start all services

```bash
make up

2. Verify services

```bash
docker-compose ps

Expected:

embedding-service → Up
indexer-service → Exited 0 (batch job)
clickhouse → healthy
opensearch → healthy


3. Run ingestion manually (if needed)

```bash
docker-compose run indexer-service


Test Embedding Service

```bash
curl http://localhost:8002/health

```bash
curl -X POST http://localhost:8002/embed \
-H "Content-Type: application/json" \
-d '{"text": "hello world"}'


Test OpenSearch

```bash
curl -k -u "admin:Opensearch2026!Aa" \
"https://localhost:9200/_cat/indices?v"


Test Search
```bash
curl -k -u "admin:Opensearch2026!Aa" \
"https://localhost:9200/github-repos/_search" \
-H "Content-Type: application/json" \
-d '{
  "size": 3,
  "query": {
    "match": {
      "description": "machine learning"
    }
  }
}'


Environment Variables

Indexer Service

```bash
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_USER=admin
CLICKHOUSE_PASSWORD=admin123


Embedding Service

```bash
RUN_ONCE=true

⚠️ Known Limitations (Level 1)
- Uses BM25 keyword search (no vector search yet)
- No semantic similarity (embeddings stored but not queried)
- Single-node OpenSearch (yellow indices expected)
- No async batching in indexer


🎯 What Level 1 Achieves

✔ Distributed microservice ingestion pipeline
✔ Embedding generation service
✔ OpenSearch indexing
✔ ClickHouse integration
✔ End-to-end data flow validated


🚀 Next Step: Level 2

Level 2 will introduce:

- kNN vector search in OpenSearch
- semantic retrieval using embeddings
- query embedding pipeline
- RAG-ready architecture