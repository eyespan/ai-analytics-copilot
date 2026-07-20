from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentStep:
    tool: str
    args: Dict[str, Any]


@dataclass
class AgentState:
    query: str
    steps: List[AgentStep] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    # 👇 ADD THESE
    last_tool: str = ""
    last_args: Dict[str, Any] = field(default_factory=dict)
    final_answer: Optional[str] = None
