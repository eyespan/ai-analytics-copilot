import time

import requests
from clickhouse_driver import Client
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

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

EMBEDDING_SERVICE = "http://embedding-service:8000"

# --------------------------------------------------
# OpenSearch
# --------------------------------------------------

OPENSEARCH_HOST = "opensearch-cluster-master.search.svc.cluster.local"
OPENSEARCH_PORT = 9200

OPENSEARCH_USER = "admin"
OPENSEARCH_PASSWORD = "Opensearch2026!Aa"

INDEX_NAME = "github-repos"


# --------------------------------------------------
# ClickHouse
# --------------------------------------------------

def get_clickhouse():

    for i in range(30):

        try:

            client = Client(
                host=CLICKHOUSE_HOST,
                port=CLICKHOUSE_PORT,
                database=CLICKHOUSE_DATABASE,
                user=CLICKHOUSE_USER,
                password=CLICKHOUSE_PASSWORD,
            )

            client.execute("SELECT 1")

            print("Connected to ClickHouse")

            return client

        except Exception as ex:

            print(f"Waiting for ClickHouse... {i} ({ex})")

            time.sleep(2)

    raise RuntimeError("ClickHouse unavailable")


# --------------------------------------------------
# OpenSearch
# --------------------------------------------------

def get_opensearch():

    for i in range(30):

        try:

            client = OpenSearch(
                hosts=[
                    {
                        "host": OPENSEARCH_HOST,
                        "port": OPENSEARCH_PORT,
                    }
                ],
                http_auth=(
                    OPENSEARCH_USER,
                    OPENSEARCH_PASSWORD,
                ),
                use_ssl=True,
                verify_certs=False,
            )

            if client.ping():

                print("Connected to OpenSearch")

                return client

        except Exception as ex:

            print(ex)

        print(f"Waiting for OpenSearch... {i}")

        time.sleep(2)

    raise RuntimeError("OpenSearch unavailable")


# --------------------------------------------------
# Embedding API
# --------------------------------------------------

def embedding(text):

    response = requests.post(
        f"{EMBEDDING_SERVICE}/embed",
        json={
            "text": text
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["embedding"]


# --------------------------------------------------
# Load repositories
# --------------------------------------------------

def load_documents(client):

    return client.execute(
        """
        SELECT
            repo_name,
            description,
            language,
            stars,
            forks
        FROM github.github_events
        """
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Connecting to ClickHouse...")

    ch = get_clickhouse()

    print("Connecting to OpenSearch...")

    os_client = get_opensearch()

    rows = load_documents(ch)

    print(f"Loaded {len(rows)} repositories")

    # -------------------------------
    # Idempotent indexing
    # -------------------------------

    if os_client.indices.exists(index=INDEX_NAME):

        print("Deleting existing index contents")

        os_client.delete_by_query(
            index=INDEX_NAME,
            body={
                "query": {
                    "match_all": {}
                }
            },
            refresh=True,
        )

    actions = []

    for row in rows:

        (
            repo_name,
            description,
            language,
            stars,
            forks,
        ) = row

        description = description or ""
        language = language or ""

        text = f"{description} {language}"

        vector = embedding(
            f"{description} {language}"
        )

        actions.append(
            {
                "_index": INDEX_NAME,
                "_id": repo_name,
                "_source": {
                    "repo_name": repo_name,
                    "description": description,
                    "language": language,
                    "stars": stars,
                    "forks": forks,
                    "embedding": vector,
                },
            }
        )

    if actions:

        success, failures = bulk(
            os_client,
            actions,
            refresh=True,
            stats_only=True,
        )

        print(f"Indexed {success} repositories")

        if failures:
            print(f"Failed documents: {failures}")

    else:

        print("No repositories found")

    print("Embedding ingestion complete")


if __name__ == "__main__":

    main()