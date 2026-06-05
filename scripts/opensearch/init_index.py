import time
import os
from opensearchpy import OpenSearch

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "Opensearch2026!Aa"

INDEX_NAME = "github-repos"

mapping = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "repo_name": {"type": "text"},
            "description": {"type": "text"},
            "language": {"type": "text"},
            "stars": {"type": "long"},
            "forks": {"type": "long"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 384
            }
        }
    }
}



def get_client():
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": 9200}],
        http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )


def wait_for_opensearch(client, retries=30):
    print("Waiting for OpenSearch...")
    for i in range(retries):
        try:
            if client.ping():
                print("OpenSearch is ready")
                return
        except Exception:
            pass
        time.sleep(2)

    raise Exception("OpenSearch did not become ready")


def create_index_if_not_exists(client):
    if client.indices.exists(index=INDEX_NAME):
        print("Deleting existing index...")
        client.indices.delete(index=INDEX_NAME)

    print(f"Creating index: {INDEX_NAME}")
    client.indices.create(index=INDEX_NAME, body=mapping)


def main():
    print("Waiting for OpenSearch...")
    client = get_client()   
    wait_for_opensearch(client)
    create_index_if_not_exists(client)
    print("Index ready for Level 3 (kNN enabled)")


if __name__ == "__main__":
    main()