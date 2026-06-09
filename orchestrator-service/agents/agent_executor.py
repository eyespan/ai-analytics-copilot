import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from agents.state import AgentState


@dataclass
class ToolResult:
    """Structured tool output — never a raw formatted string."""
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
        tool_results: Dict[str, ToolResult] = {}  # keyed by tool name

        # In run() — track failed tools and skip them
        failed_tools: set = set()

        # after storing tool result:
        tool_results[tool_name] = ToolResult(
            tool=tool_name,
            args=args,
            output=str(output),
            success=not str(output).startswith(("[DOC_ERROR]", "Tool execution error", "Tool not found"))
        )
        if not tool_results[tool_name].success:
            failed_tools.add(tool_name)

        for step_idx in range(self.max_steps):
            print(f"[AGENT] Step {step_idx + 1}")

            action = self._think(state, tool_results, context, failed_tools)
            print(f"[AGENT] Action: {action}")

            # -------------------------
            # FINAL ANSWER — exit immediately, never touch tool_name
            # -------------------------
            if action.get("final"):
                print("[AGENT] Final answer generated")
                return action.get("answer", "No answer generated")

            # -------------------------
            # Only assign tool_name AFTER confirming it's a tool action
            # -------------------------
            tool_name = action.get("tool")
            args = action.get("args") or {}

            if not tool_name:
                state.observations.append("No tool selected by model.")
                continue

            if tool_name not in self.tools.list_tools():
                state.observations.append(f"Invalid tool: {tool_name}")
                continue

            # -------------------------
            # Skip already-failed tools
            # -------------------------
            if tool_name in failed_tools:
                state.observations.append(f"{tool_name} already failed — skipping")
                state.observations.append("Please proceed to next task or finalize.")
                continue

            # -------------------------
            # Loop guard
            # -------------------------
            if (
                state.last_tool is not None
                and tool_name == state.last_tool
                and args == state.last_args
            ):
                print("[AGENT] Repeated tool call detected → stopping early")
                return self._final_answer(state, tool_results)

            # -------------------------
            # Execute
            # -------------------------
            output = self._execute(tool_name, args)
            print(f"[AGENT] Tool output: {output}")

            success = not any(
                str(output).startswith(prefix)
                for prefix in ("[DOC_ERROR]", "Tool execution error", "Tool not found")
            )

            tool_results[tool_name] = ToolResult(
                tool=tool_name,
                args=args,
                output=str(output),
                success=success
            )

            if not success:
                failed_tools.add(tool_name)

            state.observations.append(f"[{tool_name}] completed")
            state.last_tool = tool_name
            state.last_args = args

            if len(state.observations) > 20:
                print("[AGENT] Observation limit reached")
                break

        print("[AGENT] Max steps reached → synthesizing answer")
        return self._final_answer(state, tool_results)

    # =========================
    # THINK STEP
    # =========================
    def _think(
        self,
        state: AgentState,
        tool_results: Dict[str, ToolResult],
        context: str
    ) -> Dict[str, Any]:

        # task status derived from structured results, not string matching
        has_time = "get_time" in tool_results
        has_search = "search_docs" in tool_results

        resolved = self._resolve_tool_results(tool_results)

        # build failed tools summary for planner
        failed_summary = (
            "\n".join(f"- {t}: FAILED — do not retry" for t in failed_tools)
            if failed_tools else "None"
        )


        # build a clean resolved summary for the planner
        resolved = self._resolve_tool_results(tool_results)

        prompt = f"""
You are an AI planning agent.

Your job is to decide EXACTLY ONE next action.

==================================================
IMPORTANT RULES
==================================================

1. Do NOT repeat completed tasks.
2. Do NOT retry FAILED tools — accept the failure and move on.
3. Execute tasks IN ORDER as requested by the user.
4. Execute ONLY ONE tool per step.
5. If everything is done or failed → return final=true.
6. Output ONLY valid JSON.

==================================================
TASK STATUS
==================================================

- get_time completed: {has_time}
- search_docs completed: {has_search}

==================================================
FAILED TOOLS (DO NOT RETRY)
==================================================

{failed_summary}

==================================================
RESOLVED TOOL OUTPUTS
==================================================

{resolved}

==================================================
AVAILABLE TOOLS
==================================================

1. get_time
2. search_docs
3. echo

==================================================
USER REQUEST
==================================================

{state.query}

==================================================
CONTEXT
==================================================

{context}

==================================================
STOP CONDITION
==================================================

If all required tasks are complete, return:
{{
  "final": true,
  "answer": "..."
}}

Otherwise return:
{{
  "tool": "tool_name",
  "args": {{}}
}}
"""

        raw = self.model.generate(prompt)
        print(f"[AGENT] Raw model output: {raw}")

        cleaned = self._clean_json(raw)

        try:
            return json.loads(cleaned)
        except Exception:
            return {"final": True, "answer": cleaned}

    # =========================
    # RESOLVE TOOL RESULTS
    # — converts structured results to clean named values for prompts
    # — this is what prevents [get_time] leaking into LLM output
    # =========================
    def _resolve_tool_results(self, tool_results: Dict[str, ToolResult]) -> str:
        if not tool_results:
            return "No tools have been executed yet."

        lines = []
        for tool_name, result in tool_results.items():
            if result.success:
                lines.append(f"{tool_name}: {result.output}")
            else:
                lines.append(f"{tool_name}: FAILED — {result.output}")
        return "\n".join(lines)

    # =========================
    # TOOL EXECUTION
    # =========================
    def _execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        print(f"[AGENT] Executing tool: {tool_name} with args: {args}")

        tool = self.tools.get(tool_name)
        if not tool:
            return f"Tool not found: {tool_name}"

        try:
            result = tool(args)
            print(f"[AGENT] Tool result: {result}")
            return str(result)
        except Exception as e:
            print(f"[AGENT] Tool execution error: {e}")
            return f"Tool execution error: {str(e)}"

    # =========================
    # FINAL SYNTHESIS
    # — receives resolved values, never raw observation strings
    # =========================
    def _final_answer(self, state: AgentState, tool_results: Dict[str, ToolResult]) -> str:

        resolved = self._resolve_tool_results(tool_results)

        # extract specific values cleanly so the LLM doesn't have to parse
        time_value = tool_results["get_time"].output if "get_time" in tool_results else None
        search_result = tool_results["search_docs"].output if "search_docs" in tool_results else None
        search_failed = (
            "search_docs" in tool_results and not tool_results["search_docs"].success
        )

        prompt = f"""
You are a strict reasoning assistant.

You MUST only use the resolved values below.
Do NOT use external knowledge or invent facts.

==================================================
USER QUERY
==================================================
{state.query}

==================================================
RESOLVED VALUES
==================================================
{resolved}

==================================================
RULES
==================================================

{"- Current time is: " + time_value if time_value else "- No time data available."}
{"- Retrieved documents: " + search_result if search_result and not search_failed else ""}
{"- Document retrieval FAILED. Do not invent document content." if search_failed else ""}
{"- No documents were retrieved." if not search_result and not search_failed else ""}

- Summarise only what is in RESOLVED VALUES.
- Do NOT say 'I don't know' if time data exists.
- Do NOT invent PyTorch or any other external facts.

==================================================
OUTPUT
==================================================
Provide a final coherent answer based only on the resolved values above.
"""

        return self.model.generate(prompt)

    # =========================
    # JSON CLEANER
    # =========================
    def _clean_json(self, text: str) -> str:
        if not text:
            return "{}"

        text = text.strip()
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)

        return text