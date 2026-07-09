from typing import Dict, Callable, Any, Type
from pydantic import BaseModel


class ToolRegistry:

    def __init__(self):

        self.tools = {}

        self.input_models = {}

        self.output_models = {}

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        input_model: Type[BaseModel] | None = None,
        output_model: Type[BaseModel] | None = None,
    ):

        self.tools[name] = func

        if input_model:
            self.input_models[name] = input_model

        if output_model:
            self.output_models[name] = output_model

    def get(self, name):

        return self.tools.get(name)

    def get_input_model(self, name):

        return self.input_models.get(name)

    def get_output_model(self, name):

        return self.output_models.get(name)

    def list_tools(self):

        return list(self.tools.keys())
