import requests
from clickhouse_driver import Client
from datetime import datetime
import os

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))

import time
from clickhouse_driver import Client

def get_clickhouse_client():
    for i in range(20):
        try:
            client = Client(
                host="clickhouse",
                port=9000,
                database="github",
                user="admin",
                password="admin123"
            )
            client.execute("SELECT 1")
            return client
        except Exception as e:
            print(f"ClickHouse not ready, retrying... {i}")
            time.sleep(2)

    raise Exception("ClickHouse not available after retries")

client = get_clickhouse_client()

def insert_sample_data():
    data = [
        (
            datetime.now(),
            "PushEvent",
            "tensorflow/tensorflow",
            "https://github.com/tensorflow/tensorflow",
            "user1",
            "push",
            "Python",
            "Deep learning framework",
            180000,
            88000
        ),
        (
            datetime.now(),
            "WatchEvent",
            "pytorch/pytorch",
            "https://github.com/pytorch/pytorch",
            "user2",
            "star",
            "Python",
            "PyTorch deep learning library",
            75000,
            20000
        )
    ]

    client.execute("""
        INSERT INTO github.github_events
        (event_time, event_type, repo_name, repo_url,
         actor_login, action, language, description, stars, forks)
        VALUES
    """, data)

    print("Inserted sample GitHub events")

if __name__ == "__main__":
    insert_sample_data()