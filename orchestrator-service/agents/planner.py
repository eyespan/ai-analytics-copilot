import json

from prompts.planner_prompt import PLANNER_PROMPT
from schemas.planner_schema import ExecutionPlan


class Planner:

    def __init__(self, model):
        self.model = model

    def create_plan(self, query):

        #prompt = PLANNER_PROMPT.format(
        #    query=query
        #)
        prompt = PLANNER_PROMPT.replace("{query}", query)

        raw = self.model.generate(prompt)

        try:
            # extract JSON block if model adds text
            start = raw.find("{")
            end = raw.rfind("}") + 1

            if start == -1 or end == -1:
                raise ValueError("No JSON found in model output")

            json_str = raw[start:end]
            data = json.loads(json_str)

            return ExecutionPlan(**data)

        except Exception as e:
            print(f"[PLANNER] Invalid plan: {e}")
            return ExecutionPlan(steps=[])