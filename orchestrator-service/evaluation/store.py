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
            FROM evaluation_runs_all
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
                "diff": json.loads(r[10]),
                "replay": json.loads(r[11]),
                "trace": json.loads(r[12]),
                "created_at": str(r[13]),
            }
            for r in rows
        ]
    

    def append_trace(self, trace):

        self.client.execute(
            """
            INSERT INTO execution_traces_all
            (
                trace_id,
                query,
                steps,
                latency_ms,
                created_at
            )
            VALUES
            """,
            [(
                trace["trace_id"],
                trace["query"],
                json.dumps(trace.get("steps", [])),
                trace.get("latency_ms", 0),
                datetime.now(timezone.utc),
            )],
        )


    def list_traces(self, limit: int = 50):

        rows = self.client.execute(
            """
            SELECT
                trace_id,
                query,
                steps,
                latency_ms,
                created_at
            FROM execution_traces_all
            ORDER BY created_at DESC
            LIMIT %(limit)s
            """,
            {"limit": limit},
        )

        return [
            {
                "trace_id": r[0],
                "query": r[1],
                "steps": json.loads(r[2]),
                "latency_ms": r[3],
                "created_at": str(r[4]),
            }
            for r in rows
        ]