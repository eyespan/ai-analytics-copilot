from fastapi import FastAPI
#=====Level2 Addition =======
#import requests - rmoved in level 3
#from opensearchpy import OpenSearch - removed in level 3
# import os  - rmoved in level 3
#====== Level2 
#====== Level 3 Addition =======
from retrieval.vector import vector_search
from retrieval.hybrid import hybrid_search
from llm.generator import generate_answer
#====== Level 3 Addition =======
#====== Level 4 Addition =======
from retrieval.bm25 import bm25_search
from retrieval.hybrid import rrf_fusion, expand_query
from retrieval.reranker import rerank
from evaluation.metrics import (
    recall_at_k,
    reciprocal_rank
)
from evaluation.batch_eval import run_batch_eval
#====== Level 4 Addition =======


from clickhouse_client import (
    test_connection,
    get_top_repositories
)

app = FastAPI(title="RAG Service")

#Level 2 ========= Addition ========
#EMBEDDING_SERVICE = "http://embedding-service:8002/embed"

#client = OpenSearch(
#    hosts=[{"host": "opensearch", "port": 9200}],
#    http_auth=("admin", "Opensearch2026!Aa"),
#    use_ssl=True,
#    verify_certs=False
#)

# INDEX_NAME = "github-repos"
#======= Level2  ============

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "RAG Service Running"}


@app.get("/db-test")
def db_test():
    try:
        version = test_connection()
        return {
            "status": "connected",
            "clickhouse_version": version
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/top-repos")
def top_repos():
    try:
        repos = get_top_repositories()

        formatted = [
            {
                "repo_name": row[0],
                "events": row[1]
            }
            for row in repos
        ]

        return {
            "results": formatted
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    

#======Level2  Addition========
# search renoved in level3 
#====== Level2 ===========


#========== Level 3 Addition ===========
@app.post("/vector-search")
def vector_search_endpoint(payload: dict):
    try:
        query = payload["query"]
        results = vector_search(query)

        return {
            "query": query,
            "results": results
        }

    except Exception as e:
        import traceback
        print("VECTOR ERROR:", str(e))
        traceback.print_exc()
        return {"error": str(e)}
    
@app.post("/search")
def search(payload: dict):
    try:
        query = payload["query"]

        results = hybrid_search(query)

        return {
            "query": query,
            "results": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/ask")
def ask(payload: dict):
    try:
        query = payload["query"]

        # 1. Retrieve
        results = hybrid_search(query)

        # 2. Generate answer
        answer = generate_answer(query, results)

        return {
            "query": query,

            "retrieval": {
                "method": "hybrid",
                "documents_retrieved": len(results)
            },

            "answer": answer,
            "sources": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    

@app.post("/debug-retrieval")
def debug_retrieval(payload: dict):
    try:
        from retrieval.hybrid import expand_query, bm25_search, vector_search, rrf_fusion

        query = payload["query"]

        # 1. Query expansion
        expanded_query = expand_query(query)

        # 2. Independent retrieval paths
        bm25_results = bm25_search(expanded_query)
        vector_results = vector_search(expanded_query)

        # 3. Fusion
        fused_results = rrf_fusion(bm25_results, vector_results)

        return {
            "query": query,
            "expanded_query": expanded_query,
            "bm25_results": bm25_results,
            "vector_results": vector_results,
            "hybrid_results": fused_results,
            "stats": {
                "bm25_count": len(bm25_results),
                "vector_count": len(vector_results),
                "hybrid_count": len(fused_results)
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    
#========== Level 3 Addition ===========

#========== Level 4 Addition ===========
@app.post("/debug-rerank")
def debug_rerank(payload: dict):
    try:
        query = payload["query"]

        # =========================
        # Level 2 retrieval
        # =========================
        bm25_results = bm25_search(query)
        vector_results = vector_search(query)

        # =========================
        # Level 3 fusion
        # =========================
        fused_results = rrf_fusion(bm25_results, vector_results)

        # =========================
        # Level 4 reranking
        # =========================
        reranked_results = rerank(query, fused_results, top_k=10)

        return {
            "query": query,

            "retrieval": {
                "bm25_count": len(bm25_results),
                "vector_count": len(vector_results)
            },

            "fusion": {
                "method": "RRF",
                "fused_count": len(fused_results)
            },

            "rerank": {
                "method": "cross-encoder",
                "final_count": len(reranked_results)
            },

            "results": reranked_results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    

@app.post("/eval-retrieval")
def eval_retrieval(payload: dict):

    try:

        query = payload["query"]
        expected_repo = payload["expected_repo"]

        results = hybrid_search(query)

        recall = recall_at_k(
            results,
            expected_repo
        )

        rr = reciprocal_rank(
            results,
            expected_repo
        )

        return {
            "query": query,
            "expected_repo": expected_repo,
            "metrics": {
                "recall_at_k": recall,
                "reciprocal_rank": rr
            },
            "results": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    
@app.post("/eval-batch-retrieval")
def eval_batch_retrieval():
    try:
        return run_batch_eval()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    

@app.post("/eval-reranker-ab")
def eval_reranker_ab(payload: dict):
    try:
        query = payload["query"]
        expected_repo = payload["expected_repo"]

        # 1. Query expansion (Level 3)
        expanded_query = expand_query(query)

        # 2. Independent retrieval
        bm25_results = bm25_search(expanded_query)
        vector_results = vector_search(expanded_query)

        # 3. Fusion (baseline)
        fused = rrf_fusion(bm25_results, vector_results)

        # =========================
        # A) BASELINE (NO RERANK)
        # =========================
        baseline_recall = recall_at_k(fused, expected_repo)
        baseline_rr = reciprocal_rank(fused, expected_repo)

        # =========================
        # B) WITH RERANKER
        # =========================
        reranked = rerank(query, fused)

        rerank_recall = recall_at_k(reranked, expected_repo)
        rerank_rr = reciprocal_rank(reranked, expected_repo)

        # rank comparison
        def find_rank(results, repo):
            for i, r in enumerate(results):
                if r["repo_name"] == repo:
                    return i + 1
            return -1

        baseline_rank = find_rank(fused, expected_repo)
        rerank_rank = find_rank(reranked, expected_repo)

        return {
            "query": query,
            "expanded_query": expanded_query,

            "baseline": {
                "recall_at_k": baseline_recall,
                "mrr": baseline_rr,
                "rank": baseline_rank,
                "results": fused
            },

            "reranked": {
                "recall_at_k": rerank_recall,
                "mrr": rerank_rr,
                "rank": rerank_rank,
                "results": reranked
            },

            "delta": {
                "mrr_improvement": rerank_rr - baseline_rr,
                "rank_change": baseline_rank - rerank_rank
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    

@app.post("/eval-ranking-metrics")
def eval_ranking_metrics(payload: dict):

    from evaluation.metrics import recall_at_k, reciprocal_rank
    from evaluation.ranking_metrics import ndcg_at_k

    query = payload["query"]
    expected = payload["expected_repos"]
    k = payload.get("k", 10)

    expanded = expand_query(query)

    bm25 = bm25_search(expanded, k)
    vec = vector_search(expanded)

    baseline = rrf_fusion(bm25, vec)
    reranked = rerank(query, baseline.copy())

    return {
        "query": query,
        "expanded_query": expanded,

        "metrics": {
            "baseline": {
                "recall_at_k": recall_at_k(baseline, expected),
                "mrr": reciprocal_rank(baseline, expected),
                "ndcg": ndcg_at_k(baseline, expected)
            },
            "reranked": {
                "recall_at_k": recall_at_k(reranked, expected),
                "mrr": reciprocal_rank(reranked, expected),
                "ndcg": ndcg_at_k(reranked, expected)
            }
        },

        "rankings": {
            "baseline": baseline,
            "reranked": reranked
        }
    }
    
#========== Level 3 Addition ===========