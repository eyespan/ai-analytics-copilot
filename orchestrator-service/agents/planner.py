import json

from prompts.planner_prompt import PLANNER_PROMPT
from schemas.planner_schema import ExecutionPlan
from schemas.tool_schemas import TOOL_SCHEMAS


class Planner:

    MAX_PLAN_STEPS = 8

    def __init__(self, model):
        self.model = model

    def create_plan(self, query: str) -> ExecutionPlan:

        # ----------------------------------------------------
        # Build tool list dynamically from TOOL_SCHEMAS
        # ----------------------------------------------------
        tool_list = "\n".join(f"- {tool}" for tool in TOOL_SCHEMAS.keys())

        prompt = PLANNER_PROMPT.replace("{tools}", tool_list).replace("{query}", query)

        raw = self.model.generate(prompt)

        try:

            # ------------------------------------------------
            # Extract JSON block
            # ------------------------------------------------
            start = raw.find("{")
            end = raw.rfind("}") + 1

            if start == -1 or end <= start:
                raise ValueError("No JSON found in model output")

            json_str = raw[start:end]

            data = json.loads(json_str)

            # ------------------------------------------------
            # Ensure steps exists
            # ------------------------------------------------
            steps = data.get("steps", [])

            if not isinstance(steps, list):
                raise ValueError("steps must be a list")

            # ------------------------------------------------
            # Filter invalid tools
            # ------------------------------------------------
            allowed_tools = set(TOOL_SCHEMAS.keys())

            filtered_steps = []

            for step in steps:

                tool = step.get("tool")

                if tool not in allowed_tools:

                    print(f"[PLANNER] Removing invalid tool: {tool}")

                    continue

                filtered_steps.append(step)

            # ------------------------------------------------
            # Remove duplicate consecutive steps
            # ------------------------------------------------
            deduped_steps = []

            for step in filtered_steps:

                if (
                    deduped_steps
                    and deduped_steps[-1].get("tool") == step.get("tool")
                    and deduped_steps[-1].get("args", {}) == step.get("args", {})
                ):
                    continue

                deduped_steps.append(step)

            # ------------------------------------------------
            # Limit plan size
            # ------------------------------------------------
            if len(deduped_steps) > self.MAX_PLAN_STEPS:

                print(
                    f"[PLANNER] Plan exceeded "
                    f"{self.MAX_PLAN_STEPS} steps. Truncating."
                )

                deduped_steps = deduped_steps[: self.MAX_PLAN_STEPS]

            data["steps"] = deduped_steps

            # ------------------------------------------------
            # Return validated execution plan
            # ------------------------------------------------
            return ExecutionPlan(**data)

        except Exception as e:

            print(f"[PLANNER] Invalid plan: {e}")

            return ExecutionPlan(steps=[])
