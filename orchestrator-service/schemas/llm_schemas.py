from pydantic import BaseModel
from typing import Optional, Dict, Any


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