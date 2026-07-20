from dataclasses import dataclass, field
from typing import List


@dataclass
class WorkflowStepRecord:
    tool: str
    args: dict
    status: str = "pending"  # running | success | failed
    output: any = None
    latency_ms: int = 0


@dataclass
class WorkflowState:

    workflow_id: str

    query: str

    current_step: int = 0

    completed_steps: List[str] = field(default_factory=list)

    failed_steps: List[str] = field(default_factory=list)

    # NEW (optional but powerful)
    steps: List[WorkflowStepRecord] = field(default_factory=list)

    status: str = "created"

    def start(self):

        self.status = "running"

    def add_step(self, tool: str, args: dict):
        self.steps.append(WorkflowStepRecord(tool=tool, args=args))

    def complete_step(self, tool_name: str):
        self.completed_steps.append(tool_name)
        self.current_step += 1

        if self.steps:
            self.steps[-1].status = "success"

    def fail_step(self, tool_name: str):
        self.failed_steps.append(tool_name)
        self.current_step += 1

        if self.steps:
            self.steps[-1].status = "failed"

    def finish(self):

        self.status = "completed"

    def fail_workflow(self):

        self.status = "failed"
