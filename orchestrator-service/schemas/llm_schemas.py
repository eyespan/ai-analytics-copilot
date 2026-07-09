from typing import Any, Dict, Optional

from pydantic import BaseModel


class ToolAction(BaseModel):
    tool: str
    args: Dict[str, Any] = {}


class FinalAnswer(BaseModel):
    final: bool
    answer: Optional[str] = None


class ToolResultSchema(BaseModel):
    tool: str
    output: str
    success: bool


class AgentStepOutput(BaseModel):
    type: str  # "tool" | "final"
    data: Dict[str, Any]
