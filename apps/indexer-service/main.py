import os
import time

import requests
from clickhouse_driver import Client
from opensearchpy import OpenSearch


# --------------------------------------------------
# ClickHouse
# --------------------------------------------------

#CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_HOST = "clickhouse.data.svc.cluster.local"

CLICKHOUSE_PORT = 9000
CLICKHOUSE_DATABASE = "github"
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "admin123"

# --------------------------------------------------
# Embedding Service
# --------------------------------------------------

EMBEDDING_SERVICE = "http://embedding-service:80"

# --------------------------------------------------
# OpenSearch
# --------------------------------------------------

OPENSEARCH_HOST = "opensearch-cluster-master.search.svc.cluster.local"
OPENSEARCH_PORT = 9200

OPENSEARCH_USER = "admin"
OPENSEARCH_PASSWORD = "Opensearch2026!Aa"


INDEX_NAME = "github-repos"

RUN_ONCE = os.getenv("RUN_ONCE", "true").lower() == "true"


# ------------------------
# CLICKHOUSE
# ------------------------

def wait_for_clickhouse(retries=20):

    print("Waiting for ClickHouse...")

    for i in range(retries):
        try:
            client = Client(
                host=CLICKHOUSE_HOST,
                port=CLICKHOUSE_PORT,
                database=CLICKHOUSE_DATABASE,
                user=CLICKHOUSE_USER,
                password=CLICKHOUSE_PASSWORD,
            )

            client.execute("SELECT 1")

            print("ClickHouse is ready")
            return client

        except Exception as e:
            print(f"ClickHouse not ready ({i}): {e}")

        time.sleep(3)

    raise RuntimeError("ClickHouse never became ready")

clickhouse = wait_for_clickhouse()

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
# OPENSEARCH HEALTH CHECK
# ------------------------


def wait_for_opensearch(client, retries=20):
    print("Waiting for OpenSearch...")

    for _ in range(retries):
        try:
            if client.ping():
                print("OpenSearch is ready")
                return
        except Exception:
            pass

        time.sleep(3)

    raise Exception("OpenSearch not ready")


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
            r = requests.post(url, json={"text": text}, timeout=10)

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
    wait_for_opensearch(opensearch)

    query = """
    SELECT
            repo_name,
            any(description) AS description,
            any(language) AS language,
            max(stars) AS stars,
            max(forks) AS forks
        FROM github.github_events_all
        GROUP BY repo_name
    """

    rows = clickhouse.execute(query)

    print(f"Found {len(rows)} rows")

    try:

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
                "embedding": embedding,
            }

            opensearch.index(index=INDEX_NAME, id=repo_name, body=doc, refresh=True)

            print(f"Indexed: {repo_name}")

        print("Finished indexing")
    except Exception as e:
        print(f"Failed indexing {repo_name}: {e}")
        


if __name__ == "__main__":
    main()
