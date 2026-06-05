from clients.opensearch_client import opensearch
from clients.embedding_client import get_embedding

INDEX_NAME = "github-repos"
TOP_K = 5


def vector_search(query: str):

    embedding = get_embedding(query)

    response = opensearch.search(
        index=INDEX_NAME,
        body={
            "size": TOP_K,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": TOP_K
                    }
                }
            }
        }
    )

    hits = response["hits"]["hits"]

    results = []

    for h in hits:
        src = h["_source"]

        results.append({
            "repo_name": src.get("repo_name"),
            "description": src.get("description"),
            "language": src.get("language"),
            "score": h.get("_score")
        })

    return results