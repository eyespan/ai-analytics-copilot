from copy import deepcopy

from schemas.tool_schemas import TOOL_SCHEMAS
from schemas.planner_schema import PlanStep


class PlanRepairEngine:

    TOOL_ALIASES = {
        "search_document": "search_docs",
        "search": "search_docs",
        "time": "get_time",
        "clock": "get_time",
    }

    def repair(self, plan, query):

        repaired = deepcopy(plan)

        repaired.steps = self._remove_invalid_tools(repaired.steps)

        repaired.steps = self._repair_tools(repaired.steps)

        repaired.steps = self._repair_args(repaired.steps, query)

        repaired.steps = self._query_based_repair(repaired.steps, query)

        repaired.steps = self._remove_duplicates(repaired.steps)

        repaired.steps = self._inject_missing_steps(repaired.steps, query)

        return repaired

    def _repair_tools(self, steps):

        for step in steps:

            if step.tool in TOOL_SCHEMAS:
                continue

            if step.tool in self.TOOL_ALIASES:

                step.tool = self.TOOL_ALIASES[step.tool]

        return steps

    def _repair_args(self, steps, query):

        for step in steps:

            schema = TOOL_SCHEMAS.get(step.tool, {})

            args = step.args or {}

            for field, field_type in schema.items():

                if field in args:
                    continue

                if field == "query":
                    args["query"] = query

            allowed = set(schema.keys())

            args = {k: v for k, v in args.items() if k in allowed}

            step.args = args

        return steps

    def _remove_duplicates(self, steps):

        repaired = []

        previous = None

        for step in steps:

            current = (step.tool, str(step.args))

            if current == previous:
                continue

            repaired.append(step)

            previous = current

        return repaired

    def _remove_invalid_tools(self, steps):

        repaired = []

        for step in steps:

            if step.tool in TOOL_SCHEMAS:
                repaired.append(step)

            elif step.tool in self.TOOL_ALIASES:
                repaired.append(step)

        return repaired

    def _inject_missing_steps(self, steps, query):

        # q = query.lower()
        # tools = {s.tool for s in steps}

        # # --- TIME INTENT ---
        # if "time" in q and "get_time" not in tools:

        #     steps.append(
        #         PlanStep(
        #             tool="get_time",
        #             args={}
        #         )
        #     )

        return steps

    def _query_based_repair(self, steps, query):
        # q = query.lower()

        # if "time" in q:

        #     return [
        #         s for s in steps
        #         if s.tool == "get_time"
        #     ] or [
        #         PlanStep(
        #             tool="get_time",
        #             args={}
        #         )
        #     ]

        return steps
