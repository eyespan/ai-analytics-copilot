from clients.opensearch_client import opensearch
from config import INDEX_NAME, TOP_K


def bm25_search(query: str, k=TOP_K):

    size = k if k is not None else TOP_K
    size = int(size)  # 🔥 force safe type

    resp = opensearch.search(
        index=INDEX_NAME,
        body={
            "size": k,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["description", "repo_name", "language"],
                }
            },
        },
    )

    results = []

    for hit in resp["hits"]["hits"]:
        results.append(
            {
                "repo_name": hit["_source"]["repo_name"],
                "description": hit["_source"]["description"],
                "language": hit["_source"]["language"],
                "score": hit["_score"],
            }
        )

    return results
