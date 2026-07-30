import json
import os
import uuid
from datetime import datetime, timezone

from clickhouse_driver import Client


class EvaluationStore:

    def __init__(self):

        self.client = Client(
            host=os.getenv(
                "CLICKHOUSE_HOST",
                "clickhouse.data.svc.cluster.local",
            ),
            port=int(
                os.getenv(
                    "CLICKHOUSE_PORT",
                    "9000",
                )
            ),
            database="ai_evaluation",
            user="admin",
            password="admin123",
        )

    def append(self, result):

        self.client.execute(
            """
            INSERT INTO evaluation_runs
            (
                evaluation_id,
                dataset_id,
                query,
                passed,
                score,
                alignment_score,
                coverage_score,
                ordering_score,
                penalty_score,
                latency_ms,
                diff,
                replay,
                trace,
                created_at
            )
            VALUES
            """,
            [(
                str(uuid.uuid4()),
                result["id"],
                result["query"],
                1 if result["passed"] else 0,
                result["score"],
                result["score_breakdown"]["alignment_score"],
                result["score_breakdown"]["coverage_score"],
                result["score_breakdown"]["ordering_score"],
                result["score_breakdown"]["penalties"],
                self._latency(result),
                json.dumps(result["diff"]),
                json.dumps(result["replay"]),
                json.dumps(result["trace"]),
                datetime.now(timezone.utc),
            )],
        )

    def _latency(self, result):

        return sum(
            step.get("latency_ms", 0)
            for step in result["trace"]["steps"]
        )