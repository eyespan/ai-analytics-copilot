import os

from opensearchpy import OpenSearch

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")

opensearch = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": 9200}],
    http_auth=("admin", "Opensearch2026!Aa"),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)
