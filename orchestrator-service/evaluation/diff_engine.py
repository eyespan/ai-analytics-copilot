from dataclasses import dataclass
from typing import Any, Dict, List

from evaluation.types import EvalResult, StepScore


class DiffEngine:

    IGNORED_TOOLS = {"planner", "plan_repair", "final_answer"}

    # ------------------------------------------------------------
    # MAIN ENTRY (STABLE CONTRACT)
    # ------------------------------------------------------------
    def diff(
        self, expected_steps: List[Dict[str, Any]], actual_trace: List[Dict[str, Any]]
    ) -> EvalResult:

        # --------------------------------------------------------
        # 1. NORMALIZE INPUTS (CRITICAL FIX)
        # --------------------------------------------------------
        expected_steps = self._normalize_expected(expected_steps)
        actual_steps = self._normalize_actual(actual_trace)

        # --------------------------------------------------------
        # 2. ALIGN STEPS
        # --------------------------------------------------------
        alignment_result = self._align_steps(expected_steps, actual_steps)

        # --------------------------------------------------------
        # 3. SCORE MATCHES
        # --------------------------------------------------------
        step_scores = []
        total_score = 0.0

        for match in alignment_result["matches"]:
            score = self._score_step(match["expected"], match["actual"])

            step_scores.append(
                {
                    "expected": match["expected"],
                    "actual": match["actual"],
                    "score": score,
                }
            )

            total_score += score

        # --------------------------------------------------------
        # 4. HANDLE MISSING STEPS
        # --------------------------------------------------------
        missing = alignment_result["missing"]

        for m in missing:
            step_scores.append({"expected": m, "actual": None, "score": 0.0})

        # --------------------------------------------------------
        # 5. EXTRA STEPS
        # --------------------------------------------------------
        extra = alignment_result["extra"]

        # --------------------------------------------------------
        # 6. FINAL SCORE (SAFE VERSION)
        # --------------------------------------------------------
        if len(expected_steps) == 0:
            final_score = 0.0
        else:
            avg_score = total_score / max(len(alignment_result["matches"]), 1)
            coverage = len(alignment_result["matches"]) / len(expected_steps)
            penalty = 0.05 * len(extra)

            final_score = max(0.0, min(1.0, 0.7 * avg_score + 0.3 * coverage - penalty))

        passed = final_score >= 0.85 and len(missing) == 0

        # --------------------------------------------------------
        # 7. RETURN (NOW MATCHES REAL EVALRESULT)
        # --------------------------------------------------------
        return EvalResult(
            passed=passed,
            missing_steps=[m.get("tool") for m in missing],
            extra_steps=[e.get("tool") for e in extra],
            mismatched_steps=alignment_result["mismatches"],
            score=final_score,
            step_scores=[
                StepScore(expected=s["expected"], actual=s["actual"], score=s["score"])
                for s in step_scores
            ],
            alignment_score=coverage,  # or your alignment metric
            coverage_score=coverage,
        )

    # ------------------------------------------------------------
    # NORMALIZATION LAYER (CRITICAL FIX)
    # ------------------------------------------------------------
    def _normalize_expected(self, steps):
        normalized = []

        for s in steps:
            normalized.append({"tool": s.get("tool"), "args": s.get("args", {}) or {}})

        return normalized

    def _normalize_actual(self, trace):
        normalized = []

        for step in trace:
            tool = step.get("tool")

            if not tool:
                continue

            if tool in self.IGNORED_TOOLS:
                continue

            normalized.append({"tool": tool, "args": step.get("args", {}) or {}})

        return normalized

    # ------------------------------------------------------------
    # ALIGNMENT ENGINE (YOUR V2 LOGIC PRESERVED)
    # ------------------------------------------------------------
    def _align_steps(self, expected, actual):

        used = set()
        matches = []
        missing = []
        mismatches = []

        for exp in expected:

            best_score = 0.0
            best_j = None
            best_actual = None

            for j, act in enumerate(actual):

                if j in used:
                    continue

                tool_score = self._tool_score(exp["tool"], act["tool"])

                arg_score = self._arg_score(exp.get("args", {}), act.get("args", {}))

                score = tool_score * 0.6 + arg_score * 0.4

                if score > best_score:
                    best_score = score
                    best_j = j
                    best_actual = act

            if best_j is not None and best_score > 0:

                used.add(best_j)

                matches.append({"expected": exp, "actual": best_actual, "score": best_score})

                if best_score < 0.8:
                    mismatches.append(
                        {
                            "expected": exp,
                            "actual": best_actual,
                            "reason": "partial mismatch",
                            "score": best_score,
                        }
                    )

            else:
                missing.append(exp)

        extra = [actual[i] for i in range(len(actual)) if i not in used]

        return {
            "matches": matches,
            "missing": missing,
            "extra": extra,
            "mismatches": mismatches,
        }

    # ------------------------------------------------------------
    # TOOL SCORE
    # ------------------------------------------------------------
    def _tool_score(self, expected_tool: str, actual_tool: str) -> float:
        return 1.0 if expected_tool == actual_tool else 0.0

    # ------------------------------------------------------------
    # ARG SCORE
    # ------------------------------------------------------------
    def _arg_score(self, expected: Dict, actual: Dict) -> float:

        if expected == actual:
            return 1.0

        if not expected:
            return 1.0

        if not actual:
            return 0.0

        keys = set(expected.keys()) | set(actual.keys())
        matches = 0

        for k in keys:
            if expected.get(k) == actual.get(k):
                matches += 1

        return matches / len(keys)

    # ------------------------------------------------------------
    # STEP SCORE (SAFE + SIMPLE)
    # ------------------------------------------------------------
    def _score_step(self, expected: dict, actual: dict) -> float:

        if not expected or not actual:
            return 0.0

        if expected.get("tool") != actual.get("tool"):
            return 0.0

        tool_score = 1.0

        expected_args = expected.get("args", {}) or {}
        actual_args = actual.get("args", {}) or {}

        if expected_args == actual_args:
            arg_score = 1.0
        else:
            if not expected_args:
                arg_score = 1.0
            else:
                common = set(expected_args.keys()) & set(actual_args.keys())

                if not common:
                    arg_score = 0.0
                else:
                    arg_score = sum(
                        1 for k in common if expected_args.get(k) == actual_args.get(k)
                    ) / len(expected_args)

        return 0.7 * tool_score + 0.3 * arg_score
