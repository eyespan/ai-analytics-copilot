from typing import List, Dict, Any
from evaluation.diff_engine import DiffEngine


class EvaluationRunner:

    def __init__(self, agent):
        self.agent = agent
        self.diff_engine = DiffEngine()

    # ------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------
    def run_dataset(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:

        results = []

        total_score = 0.0
        passed_count = 0

        for item in dataset:

            print(f"[EVAL] Running: {item['id']}")

            result = self.evaluate(item)

            results.append(result)

            total_score += result.get("score", 0.0)

            if result["passed"]:
                passed_count += 1

        return {
            "summary": {
                "total": len(dataset),
                "passed": passed_count,
                "failed": len(dataset) - passed_count,
                "score": total_score / len(dataset) if dataset else 0.0
            },
            "results": results
        }

    # ------------------------------------------------------------
    # SINGLE ITEM EVALUATION
    # ------------------------------------------------------------
    def evaluate(self, item: Dict[str, Any]) -> Dict[str, Any]:

        query = item["query"]
        expected_steps = item.get("expected_steps", [])

        print("[EVAL] Running evaluation")

        # -----------------------------
        # 1. AGENT EXECUTION
        # -----------------------------
        agent_result = self.agent.run(query)

        trace = agent_result["trace"]

        # -----------------------------
        # 2. REPLAY EXECUTION
        # -----------------------------
        replay_result = self.agent.run(query)

        replay_trace = replay_result["trace"]

        # -----------------------------
        # 3. DIFF ENGINE (ALIGNMENT SCORE)
        # -----------------------------
        diff_result = self.diff_engine.diff(
            expected_steps=expected_steps,
            actual_trace=trace["steps"]
        )

        # -----------------------------
        # 4. REPLAY COMPARISON
        # -----------------------------
        replay_comparison = self._compare_traces(
            trace["steps"],
            replay_trace["steps"]
        )

        # -----------------------------
        # 5. SCORE BREAKDOWN
        # -----------------------------
        score_breakdown = self._build_score_breakdown(
            diff_result,
            replay_comparison
        )

        final_score = score_breakdown["final_score"]

        passed = (
            final_score >= 0.85
            and len(diff_result.missing_steps) == 0
        )

        # -----------------------------
        # 6. FINAL REPORT
        # -----------------------------
        return {
            "id": item["id"],
            "query": query,

            "passed": passed,
            "score": final_score,

            "score_breakdown": score_breakdown,

            "step_scores": diff_result.step_scores,

            "diff": {
                "missing": diff_result.missing_steps,
                "extra": diff_result.extra_steps,
                "mismatches": diff_result.mismatched_steps
            },

            "replay": replay_comparison,

            "trace": trace
        }

    # ------------------------------------------------------------
    # REPLAY COMPARISON
    # ------------------------------------------------------------
    def _compare_traces(self, original: List[Dict], replay: List[Dict]) -> Dict[str, Any]:

        original_tools = [s["tool"] for s in original if "tool" in s]
        replay_tools = [s["tool"] for s in replay if "tool" in s]

        return {
            "deterministic": original_tools == replay_tools,
            "trace_match": original == replay,
            "divergence_points": self._find_divergence(original, replay)
        }

    def _find_divergence(self, a, b):

        divergences = []
        min_len = min(len(a), len(b))

        for i in range(min_len):

            if a[i].get("tool") != b[i].get("tool"):
                divergences.append({
                    "step": i + 1,
                    "expected": a[i].get("tool"),
                    "actual": b[i].get("tool")
                })

        return divergences

    # ------------------------------------------------------------
    # SCORE BREAKDOWN ENGINE
    # ------------------------------------------------------------
    def _build_score_breakdown(self, diff_result, replay_comparison):

        alignment_score = getattr(diff_result, "score", 1.0)

        coverage_score = 1.0 - (
            len(diff_result.missing_steps) * 0.1
        )

        ordering_score = 1.0 if replay_comparison["deterministic"] else 0.8

        penalty = len(diff_result.extra_steps) * 0.05

        final_score = max(
            0.0,
            min(
                1.0,
                0.5 * alignment_score +
                0.3 * coverage_score +
                0.2 * ordering_score -
                penalty
            )
        )

        return {
            "alignment_score": alignment_score,
            "coverage_score": coverage_score,
            "ordering_score": ordering_score,
            "penalties": penalty,
            "final_score": final_score
        }