# schemas/planner_schema.py

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)
    description: str | None = None


class ExecutionPlan(BaseModel):
    steps: List[PlanStep]
