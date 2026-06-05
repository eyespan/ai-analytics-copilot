from fastapi import FastAPI
#=====Level2 Addition =======
#import requests - rmoved in level 3
#from opensearchpy import OpenSearch - removed in level 3
# import os  - rmoved in level 3

#====== Level2 
#====== Level 3 Addition =======
from retrieval.vector import vector_search
from retrieval.hybrid import hybrid_search
#====== Level 3 Addition =======

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
    
#========== Level 3 Addition ===========