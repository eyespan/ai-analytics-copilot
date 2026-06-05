from clickhouse_driver import Client
from opensearchpy import OpenSearch
import requests
import os
import time

# ------------------------
# ENV CONFIG
# ------------------------

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin123")

# IMPORTANT: docker internal DNS (NOT localhost)
EMBEDDING_SERVICE = os.getenv(
    "EMBEDDING_SERVICE",
    "http://embedding-service:8002"
)

OPENSEARCH_HOST = "opensearch"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASSWORD = "Opensearch2026!Aa"

INDEX_NAME = "github-repos"

RUN_ONCE = os.getenv("RUN_ONCE", "true").lower() == "true"


# ------------------------
# CLICKHOUSE
# ------------------------

clickhouse = Client(
    host=CLICKHOUSE_HOST,
    user=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database="github"
)


# ------------------------
# OPENSEARCH
# ------------------------

opensearch = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": 9200}],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)


# ------------------------
# EMBEDDING HEALTH CHECK
# ------------------------

def wait_for_embedding_service(retries=20, delay=3):
    print("Waiting for embedding service...")

    url = f"{EMBEDDING_SERVICE}/health"

    for i in range(retries):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print("Embedding service is ready")
                return
        except Exception as e:
            print(f"Embedding not ready ({i}): {e}")

        time.sleep(delay)

    raise RuntimeError("Embedding service never became ready")


# ------------------------
# EMBEDDING CALL
# ------------------------

def get_embedding(text: str):
    url = f"{EMBEDDING_SERVICE}/embed"

    for attempt in range(3):
        try:
            r = requests.post(
                url,
                json={"text": text},
                timeout=10
            )

            if r.status_code == 200:
                return r.json()["embedding"]

        except Exception as e:
            print(f"Embedding retry {attempt}: {e}")
            time.sleep(2)

    raise RuntimeError(f"Failed to get embedding for text: {text[:50]}")


# ------------------------
# MAIN
# ------------------------

def main():

    if not RUN_ONCE:
        print("RUN_ONCE disabled, exiting")
        return

    wait_for_embedding_service()

    query = """
    SELECT repo_name, description, language, stars, forks
    FROM github.github_events
    """

    rows = clickhouse.execute(query)

    print(f"Found {len(rows)} rows")

    for row in rows:
        repo_name, description, language, stars, forks = row

        if not description:
            continue

        text = f"{repo_name} {description} {language}"
        embedding = get_embedding(text)

        doc = {
            "repo_name": repo_name,
            "description": description,
            "language": language,
            "stars": stars,
            "forks": forks,
            "embedding": embedding
        }

        opensearch.index(
            index=INDEX_NAME,
            id=repo_name,
            body=doc
        )

        print(f"Indexed: {repo_name}")

    print("Finished indexing")


if __name__ == "__main__":
    main()