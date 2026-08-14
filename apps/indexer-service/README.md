# Indexer Service

## Purpose

`apps/indexer-service` converts repository records in ClickHouse into searchable/vector documents in OpenSearch.

Its core data path is:

```text
ClickHouse
    |
    v
Indexer
    |
    v
Embedding Service
    |
    v
OpenSearch
```

## Source

```text
apps/indexer-service/
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Data Sources

The service connects to ClickHouse using:

```text
Host: clickhouse.data.svc.cluster.local
Port: 9000
Database: github
```

The current source also contains ClickHouse credentials directly in the Python configuration.

> **Security note:** these credentials should be externalised into Kubernetes Secrets or another secure configuration mechanism before treating the implementation as production-safe.

## Source Query

The indexer reads repository aggregates from:

```sql
github.github_events_all
```

using:

```sql
SELECT
    repo_name,
    any(description) AS description,
    any(language) AS language,
    max(stars) AS stars,
    max(forks) AS forks
FROM github.github_events_all
GROUP BY repo_name
```

## Document Preparation

For each repository:

```text
repo_name
description
language
stars
forks
```

are assembled into embedding text:

```text
<repo_name> <description> <language>
```

## Embedding Service

The indexer calls:

```text
http://embedding-service:80/embed
```

with:

```json
{
  "text": "<repository text>"
}
```

It retries embedding requests up to three times.

## OpenSearch

The current OpenSearch configuration is:

```text
Host:
opensearch-cluster-master.search.svc.cluster.local

Port:
9200

Index:
github-repos
```

Documents contain:

```text
repo_name
description
language
stars
forks
embedding
```

The repository name is used as the OpenSearch document ID.

## Startup Dependencies

The service waits for:

1. ClickHouse
2. embedding service
3. OpenSearch

before indexing.

ClickHouse is checked with:

```sql
SELECT 1
```

OpenSearch is checked with `ping()`.

Embedding service is checked through:

```text
GET /health
```

## Execution Mode

The service reads:

```text
RUN_ONCE
```

with default:

```text
true
```

If `RUN_ONCE` is false, the current implementation prints a message and exits rather than running a continuous indexing loop.

## Indexing Behaviour

Each valid repository is indexed with:

```python
opensearch.index(
    index=INDEX_NAME,
    id=repo_name,
    body=doc,
    refresh=True,
)
```

The service therefore performs immediate refreshes for indexed documents.

## Failure Handling

Embedding failures are retried.

The main indexing loop catches an exception and prints the repository that failed.

The current implementation does not provide a separate HTTP API for triggering an indexing run; the indexing operation occurs when the container process executes `main()`.

## Security Notes

The supplied source contains:

- ClickHouse username/password
- OpenSearch username/password

and disables OpenSearch certificate verification:

```text
verify_certs=False
```

These are implementation details that should be treated as development/deployment hardening items, not recommended production security defaults.

## Relationship to RAG

The indexer prepares the data consumed by vector/hybrid retrieval.

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
    |
    v
RAG Service
```

## Level 7

The service is suitable for Kubernetes execution but its current implementation is a run-once indexing workload rather than a continuously running indexing API.

That distinction should be preserved when extending the Level 7 platform.
