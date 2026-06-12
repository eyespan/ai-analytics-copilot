from typing import Dict, Any
from agents.agent_executor import AgentExecutor


class TraceReplayEngine:

    def __init__(self, executor: AgentExecutor):
        self.executor = executor

    def replay(self, query: str, expected_trace: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Replay execution for evaluation.

        If expected_trace is provided, it can be used for guided validation.
        """

        print("[REPLAY] Starting trace replay")

        # Run fresh execution (deterministic baseline)
        result = self.executor.run(
            query=query,
            context=""
        )

        # Optional: attach expected trace for downstream diff engine
        if expected_trace:
            result["expected_trace"] = expected_trace

        print("[EVAL] Replay result:")
        print(result)

        return result