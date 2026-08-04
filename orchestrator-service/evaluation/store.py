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
    
    def list_runs(self, limit: int = 100):

        rows = self.client.execute(
            """
            SELECT
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
            FROM evaluation_runs
            ORDER BY created_at DESC
            LIMIT %(limit)s
            """,
            {"limit": limit},
        )

        return [
            {
                "evaluation_id": r[0],
                "dataset_id": r[1],
                "query": r[2],
                "passed": bool(r[3]),
                "score": r[4],
                "alignment_score": r[5],
                "coverage_score": r[6],
                "ordering_score": r[7],
                "penalty_score": r[8],
                "latency_ms": r[9],
                "diff": r[10],
                "replay": r[11],
                "trace": r[12],
                "created_at": str(r[13]),
            }
            for r in rows
        ]