from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ExpectedStep:
    tool: str
    args: Dict[str, Any]


@dataclass
class StepScore:
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    score: float


@dataclass
class EvalResult:
    # ---------------- existing fields (DO NOT REMOVE) ----------------
    passed: bool
    missing_steps: List[str]
    extra_steps: List[str]
    mismatched_steps: List[Dict[str, Any]]

    # ---------------- V2 safe extensions ----------------
    score: float = 0.0

    step_scores: List[StepScore] = field(default_factory=list)

    alignment_score: float = 0.0
    coverage_score: float = 0.0
