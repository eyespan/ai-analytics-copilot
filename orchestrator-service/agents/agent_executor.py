import json
import re
from typing import Dict, Any, Set
from dataclasses import dataclass

from agents.state import AgentState


@dataclass
class ToolResult:
    tool: str
    args: Dict[str, Any]
    output: str
    success: bool


class AgentExecutor:

    def __init__(self, model, tool_registry, max_steps: int = 5):
        self.model = model
        self.tools = tool_registry
        self.max_steps = max_steps

    def run(self, query: str, context: str = "") -> str:

        state = AgentState(query=query)

        tool_results: Dict[str, ToolResult] = {}

        # failed tool names only
        failed_tools: Set[str] = set()

        for step_idx in range(self.max_steps):

            print(f"[AGENT] Step {step_idx + 1}")

            #
            # HARD STOP:
            # if all required tasks are already complete or failed
            #
            if self._all_tasks_finished(query, tool_results, failed_tools):
                print("[AGENT] All tasks completed/failed")
                return self._final_answer(state, tool_results)

            action = self._think(
                state=state,
                tool_results=tool_results,
                context=context,
                failed_tools=failed_tools
            )

            print(f"[AGENT] Action: {action}")

            #
            # model explicitly finalized
            #
            if action.get("final"):
                print("[AGENT] Final answer generated")
                return action.get("answer", "No answer generated")

            tool_name = action.get("tool")
            args = action.get("args") or {}

            if not tool_name:
                state.observations.append("No tool selected.")
                continue

            #
            # invalid tool
            #
            if tool_name not in self.tools.list_tools():
                state.observations.append(f"Invalid tool: {tool_name}")
                continue

            #
            # HARD FAIL GUARD
            #
            if tool_name in failed_tools:

                print(
                    f"[AGENT] Tool {tool_name} already failed -> skipping"
                )

                state.observations.append(
                    f"{tool_name} already failed"
                )

                continue

            #
            # HARD LOOP GUARD
            #
            if tool_name == state.last_tool:

                print(
                    f"[AGENT] Repeated tool call detected ({tool_name})"
                )

                return self._final_answer(
                    state,
                    tool_results
                )

            #
            # EXECUTE
            #
            output = self._execute(
                tool_name,
                args
            )

            print(f"[AGENT] Tool output: {output}")

            success = not any(
                str(output).startswith(prefix)
                for prefix in (
                    "[DOC_ERROR]",
                    "Tool execution error",
                    "Tool not found"
                )
            )

            tool_results[tool_name] = ToolResult(
                tool=tool_name,
                args=args,
                output=str(output),
                success=success
            )

            if not success:
                failed_tools.add(tool_name)

            #
            # store observation
            #
            state.observations.append(
                f"[{tool_name}] {output}"
            )

            state.last_tool = tool_name
            state.last_args = args

            if len(state.observations) > 20:
                print("[AGENT] Observation limit reached")
                break

        print("[AGENT] Max steps reached → synthesizing answer")

        return self._final_answer(
            state,
            tool_results
        )

    #
    # ------------------------------------------------------------------
    #

    def _all_tasks_finished(
        self,
        query: str,
        tool_results: Dict[str, ToolResult],
        failed_tools: Set[str]
    ) -> bool:

        q = query.lower()

        needs_time = (
            "time" in q
        )

        needs_search = (
            "search" in q
            or "document" in q
            or "docs" in q
            or "pytorch" in q
        )

        time_done = (
            "get_time" in tool_results
            or "get_time" in failed_tools
        )

        search_done = (
            "search_docs" in tool_results
            or "search_docs" in failed_tools
        )

        if needs_time and not time_done:
            return False

        if needs_search and not search_done:
            return False

        return True

    #
    # ------------------------------------------------------------------
    #

    def _think(
        self,
        state: AgentState,
        tool_results: Dict[str, ToolResult],
        context: str,
        failed_tools: Set[str]
    ) -> Dict[str, Any]:

        resolved = self._resolve_tool_results(
            tool_results
        )

        failed_summary = (
            "\n".join(
                f"- {t}: FAILED"
                for t in failed_tools
            )
            if failed_tools
            else "None"
        )

        prompt = f"""
You are an AI planning agent.

You are an AI planning agent.

Your job is to decide EXACTLY ONE next action.

==================================================
CRITICAL OUTPUT RULES
==================================================

Return EXACTLY ONE JSON object.

VALID:
{{"tool":"get_time","args":{{}}}}

VALID:
{{"tool":"search_docs","args":{{"query":"pytorch"}}}}

VALID:
{{"final":true,"answer":"..."}}

INVALID:
{{"tool":"get_time","args":{{}}}}
{{"tool":"search_docs","args":{{}}}}

INVALID:
Tool: get_time

INVALID:
Explanation followed by JSON

Return ONLY ONE JSON object and NOTHING else.


==================================================
IMPORTANT RULES
==================================================

- NEVER retry failed tools.
- NEVER repeat the previous tool.
- If all tasks are completed or failed:
  return final=true.

FAILED TOOLS:
{failed_summary}

TOOL RESULTS:
{resolved}

AVAILABLE TOOLS:
1. get_time
2. search_docs
3. echo

USER REQUEST:
{state.query}

CONTEXT:
{context}

OUTPUT JSON ONLY

Tool:
{{
  "tool":"tool_name",
  "args":{{}}
}}

Final:
{{
  "final":true,
  "answer":"..."
}}
"""

        raw = self.model.generate(prompt)

        json_objects = re.findall(
            r"\{[\s\S]*?\}",
            raw
        )

        if len(json_objects) > 1:
            print(
                f"[AGENT WARNING] Model returned "
                f"{len(json_objects)} JSON objects. "
                f"Using first object only."
            )

        cleaned = self._extract_first_json(raw)

        try:
            return json.loads(cleaned)
        except Exception as e:
            print("[AGENT] JSON parse failed:", e)
            return {
            "final": True,
            "answer": "Planner produced invalid JSON."
        }

    #
    # ------------------------------------------------------------------
    #

    def _resolve_tool_results(
        self,
        tool_results: Dict[str, ToolResult]
    ) -> str:

        if not tool_results:
            return "No tools executed."

        lines = []

        for tool_name, result in tool_results.items():

            if result.success:
                lines.append(
                    f"{tool_name}: {result.output}"
                )
            else:
                lines.append(
                    f"{tool_name}: FAILED - {result.output}"
                )

        return "\n".join(lines)

    #
    # ------------------------------------------------------------------
    #

    def _execute(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ) -> str:

        print(
            f"[AGENT] Executing tool: {tool_name}"
        )

        print(
            f"[AGENT] Tool args: {args}"
        )

        tool = self.tools.get(tool_name)

        if not tool:
            return f"Tool not found: {tool_name}"

        try:

            result = tool(args)

            print(
                f"[AGENT] Tool result: {result}"
            )

            return str(result)

        except Exception as e:

            print(
                f"[AGENT] Tool execution error: {e}"
            )

            return (
                f"Tool execution error: {str(e)}"
            )

    #
    # ------------------------------------------------------------------
    #

    def _final_answer(
        self,
        state: AgentState,
        tool_results: Dict[str, ToolResult]
    ) -> str:

        resolved = self._resolve_tool_results(
            tool_results
        )

        prompt = f"""
You are a strict reasoning assistant.

Use ONLY the information below.

USER QUERY:
{state.query}

RESOLVED VALUES:
{resolved}

RULES:

- Use only resolved values.
- Do not use external knowledge.
- Do not invent document contents.
- If document retrieval failed, explicitly say so.
- If time exists, include it.

Generate a concise final answer.
"""

        return self.model.generate(prompt)

    #
    # ------------------------------------------------------------------
    #

    def _extract_first_json(self, text: str) -> str:
        if not text:
            return "{}"

        text = text.replace("```json", "").replace("```", "").strip()

        start = text.find("{")
        if start == -1:
            return "{}"

        depth = 0

        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1

                if depth == 0:
                    return text[start:i + 1]

        return "{}"