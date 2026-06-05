from retrieval.bm25 import bm25_search
from retrieval.vector import vector_search


def rrf_fusion(bm25_results, vector_results, k=60):
    scores = {}

    def add(results, weight=1.0):
        for rank, item in enumerate(results):
            key = item["repo_name"]
            score = weight * (1 / (k + rank))

            if key not in scores:
                scores[key] = {
                    "repo_name": item["repo_name"],
                    "description": item["description"],
                    "language": item["language"],
                    "score": 0
                }

            scores[key]["score"] += score

    add(bm25_results, weight=1.0)
    add(vector_results, weight=1.0)

    return sorted(scores.values(), key=lambda x: x["score"], reverse=True)


def hybrid_search(query: str):
    bm25 = bm25_search(query)
    vector = vector_search(query)

    return rrf_fusion(bm25, vector)