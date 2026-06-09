from typing import Dict, Callable, Any


class ToolRegistry:
    """
    Simple registry of tools the agent can call.
    """

    def __init__(self):
        self.tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]):
        self.tools[name] = func

    def get(self, name: str):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())