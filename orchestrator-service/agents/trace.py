from dataclasses import dataclass, field
from typing import Any, Dict, List
import time
import uuid


class TraceEventType:
    TOOL_EXECUTION = "tool_execution"
    TOOL_SKIPPED = "tool_skipped"
    TOOL_FAILED = "tool_failed"
    FINAL_ANSWER = "final_answer"
    PLAN = "plan"

@dataclass
class StepTrace:
    step: int
    tool: str = ""
    event_type: str = TraceEventType.TOOL_EXECUTION
    args: Dict[str, Any] = field(default_factory=dict)
    output: str = ""
    success: bool = True
    latency_ms: int = 0


@dataclass
class AgentTrace:
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    start_time: float = field(default_factory=time.time)
    steps: List[StepTrace] = field(default_factory=list)

    def add_step(self, step: StepTrace):
        step.step = len(self.steps) + 1
        self.steps.append(step)

    def add_step(self, step: StepTrace):
            step.step = len(self.steps) + 1
            self.steps.append(step)

    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "start_time": self.start_time,
            "steps": [s.__dict__ for s in self.steps]
        }
