from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from clickhouse_driver import Client
import os, json


class ConversationStore:
    """
    Level 5 Memory Layer

    Stores:
    - user queries
    - assistant responses
    - session context
    - optional metadata (model, latency, retrieval stats)
    """

    def __init__(self):

        self.client = Client(
            host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
            port=int(os.getenv("CLICKHOUSE_PORT", "9000")),
            database="ai_memory",
            user="admin",
            password="admin123",
        )

    # =========================
    # WRITE MEMORY
    # =========================
    def append(
        self,
        session_id: str,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):

        event_id = str(uuid.uuid4())
        ts = datetime.now(timezone.utc)

        self.client.execute(
            """
            INSERT INTO ai_memory
            (event_id, session_id, timestamp, query, response, metadata)
            VALUES
            """,
            [(event_id, session_id, ts, query, response, json.dumps(metadata or {}))],
        )

    # =========================
    # READ SHORT-TERM MEMORY
    # =========================
    def get(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:

        rows = self.client.execute(
            """
            SELECT session_id, timestamp, query, response, metadata
            FROM ai_memory
            WHERE session_id = %(session_id)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
            """,
            {"session_id": session_id, "limit": limit},
        )

        return [
            {
                "session_id": r[0],
                "timestamp": r[1],
                "query": r[2],
                "response": r[3],
                "metadata": r[4],
            }
            for r in rows
        ]

    # =========================
    # CLEAR SESSION MEMORY
    # =========================
    def clear(self, session_id: str):

        self.client.execute(
            """
            ALTER TABLE ai_memory DELETE WHERE session_id = %(session_id)s
            """,
            {"session_id": session_id},
        )
