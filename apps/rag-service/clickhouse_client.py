from clickhouse_driver import Client
import os

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin123")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "github")

client = Client(
    host=CLICKHOUSE_HOST,
    user=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DB,
)


def test_connection():
    return client.execute("SELECT version()")


def get_top_repositories(limit=10):
    query = f"""
    SELECT
        repo_name,
        count(*) as events
    FROM github.github_events
    GROUP BY repo_name
    ORDER BY events DESC
    LIMIT {limit}
    """

    return client.execute(query)
