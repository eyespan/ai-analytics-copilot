from fastapi import FastAPI
from clickhouse_client import (
    test_connection,
    get_top_repositories
)

app = FastAPI(title="RAG Service")


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