import os
import time
from datetime import datetime

from clickhouse_driver import Client

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))


def get_clickhouse_client():
    for i in range(20):
        try:
            client = Client(
                host="clickhouse",
                port=9000,
                database="github",
                user="admin",
                password="admin123",
            )
            client.execute("SELECT 1")
            return client
        except Exception:
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
            88000,
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
            20000,
        ),
        # =========================
        # Level 4 Expansion Set
        # =========================
        (
            datetime.now(),
            "PushEvent",
            "keras-team/keras",
            "https://github.com/keras-team/keras",
            "user3",
            "push",
            "Python",
            "High-level neural network API for TensorFlow",
            65000,
            17000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "apache/mxnet",
            "https://github.com/apache/mxnet",
            "user4",
            "push",
            "C++",
            "Deep learning framework designed for scalability",
            19000,
            6000,
        ),
        (
            datetime.now(),
            "WatchEvent",
            "huggingface/transformers",
            "https://github.com/huggingface/transformers",
            "user5",
            "star",
            "Python",
            "Transformer models library for NLP and deep learning",
            120000,
            25000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "scikit-learn/scikit-learn",
            "https://github.com/scikit-learn/scikit-learn",
            "user6",
            "push",
            "Python",
            "Machine learning library for classical algorithms",
            60000,
            23000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "pandas-dev/pandas",
            "https://github.com/pandas-dev/pandas",
            "user7",
            "push",
            "Python",
            "Data analysis and manipulation library",
            41000,
            15000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "numpy/numpy",
            "https://github.com/numpy/numpy",
            "user8",
            "push",
            "Python",
            "Scientific computing library for arrays and math",
            50000,
            18000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "apache/spark",
            "https://github.com/apache/spark",
            "user9",
            "push",
            "Scala",
            "Distributed data processing engine",
            42000,
            22000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "docker/docker-ce",
            "https://github.com/docker/docker-ce",
            "user10",
            "push",
            "Go",
            "Containerization platform for application deployment",
            65000,
            12000,
        ),
        (
            datetime.now(),
            "PushEvent",
            "kubernetes/kubernetes",
            "https://github.com/kubernetes/kubernetes",
            "user11",
            "push",
            "Go",
            "Container orchestration system for scaling applications",
            105000,
            38000,
        ),
    ]

    client.execute(
        """
        INSERT INTO github.github_events
        (event_time, event_type, repo_name, repo_url,
         actor_login, action, language, description, stars, forks)
        VALUES
    """,
        data,
    )

    print("Inserted sample GitHub events")


if __name__ == "__main__":
    insert_sample_data()
