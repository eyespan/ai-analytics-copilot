from evaluation.diff_engine import DiffEngine
from evaluation.trace_replay import TraceReplayEngine


class Evaluator:

    def __init__(self, executor):
        self.replay_engine = TraceReplayEngine(executor)
        self.diff_engine = DiffEngine()

    def evaluate(self, query: str, expected_plan: list):

        print("[EVAL] Running evaluation")

        # 1. run system
        result = self.replay_engine.replay(query)

        print("[EVAL] Replay result:")
        print(result)

        # trace = result["trace"]["steps"]
        trace_obj = result.get("trace", {})

        if "steps" not in trace_obj:
            return {
                "query": query,
                "passed": False,
                "error": (
                    "Expected agent trace but "
                    f"received trace type={trace_obj.get('type')}"
                ),
                "trace": trace_obj
            }

        trace = trace_obj["steps"]

        # 2. diff expected vs actual
        diff_result = self.diff_engine.diff(
            expected_plan,
            trace
        )

        return {
            "query": query,
            "passed": diff_result.passed,
            "missing_steps": diff_result.missing_steps,
            "extra_steps": diff_result.extra_steps,
            "mismatches": diff_result.mismatched_steps,
            "trace": result["trace"]
        }