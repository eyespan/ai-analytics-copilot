from retrieval.bm25 import bm25_search
from retrieval.vector import vector_search
#====== Level 4 Addition =======
from retrieval.reranker import rerank
#====== Level 4 Addition =======



# -----------------------
# QUERY EXPANSION LAYER
# -----------------------
def expand_query(query: str) -> str:
    expansions = {
        "neural networks": "deep learning neural networks AI machine learning",
        "machine learning": "ML AI models training inference",
        "framework": "library toolkit API implementation",
        "python": "Python programming language"
    }

    q = query.lower()

    for key, value in expansions.items():
        if key in q:
            return query + " " + value

    return query


# -----------------------
# RRF FUSION
# -----------------------
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

    add(bm25_results, weight=0.7)
    add(vector_results, weight=1.3)

    return sorted(scores.values(), key=lambda x: x["score"], reverse=True)


# -----------------------
# MAIN HYBRID SEARCH
# -----------------------
def hybrid_search(query: str):
    expanded_query = expand_query(query)

    bm25 = bm25_search(expanded_query)
    vector = vector_search(expanded_query)

    from retrieval.reranker import rerank

    results = rrf_fusion(bm25, vector)

    # LEVEL 4 ADDITION
    results = rerank(query, results, top_k=10)

    print("\n[DEBUG RERANK]")
    for r in results[:3]:
        print(r["repo_name"], r.get("rerank_score"))
    #====== Level 4 Addition =======

    return results