from fastapi import FastAPI
#=====Level2 Addition =======
import requests
from opensearchpy import OpenSearch
import os
#====== Level2 

from clickhouse_client import (
    test_connection,
    get_top_repositories
)

app = FastAPI(title="RAG Service")

#Level 2 ========= Addition ========
EMBEDDING_SERVICE = "http://embedding-service:8002/embed"

client = OpenSearch(
    hosts=[{"host": "opensearch", "port": 9200}],
    http_auth=("admin", "Opensearch2026!Aa"),
    use_ssl=True,
    verify_certs=False
)

INDEX_NAME = "github-repos"
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

@app.post("/search")
def search(payload: dict):
    try:
        query = payload["query"]

        # optional: still generate embedding (future use)
        requests.post(
            EMBEDDING_SERVICE,
            json={"text": query}
        )

        resp = client.search(
            index=INDEX_NAME,
            body={
                "size": 5,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "description",
                            "repo_name",
                            "language"
                        ]
                    }
                }
            }
        )

        hits = [
            {
                "repo_name": h["_source"]["repo_name"],
                "description": h["_source"]["description"],
                "score": h["_score"]
            }
            for h in resp["hits"]["hits"]
        ]

        return {
            "query": query,
            "results": hits
        }

    except Exception as e:
        import traceback
        print("RAG ERROR:", str(e))
        traceback.print_exc()
        return {"error": str(e)}
#====== Level2 ===========