import json
import re
import time
from typing import Dict, Any, Set
from dataclasses import dataclass

from agents.state import AgentState
from agents.trace import AgentTrace, StepTrace, TraceEventType
from core.structured_output import StructuredOutputValidator, StructuredOutputError
from schemas.llm_schemas import ToolAction, FinalAnswer
from agents.planner import Planner  # Ensure Planner is defined in agents.planner module



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
        

    def run(self, query: str, context: str = ""):

        state = AgentState(query=query)
        self.trace = AgentTrace(query=query)

        tool_results: Dict[str, ToolResult] = {}
        failed_tools: Set[str] = set()

        step_id = 0  # ✅ FIX 1: stable step counter

        #
        # CREATE EXECUTION PLAN
        #
        planner = Planner(self.model)

        try:
            plan = planner.create_plan(query)
        except Exception as e:
            return self._fallback_answer(f"Planner error: {str(e)}")

        # ----------------------------
        # FIX 2: PLAN VALIDATION
        # ----------------------------
        if not plan or not plan.steps:
            return self._fallback_answer("Empty plan")

        self._validate_plan(plan)   # ✅ NEW (important for Phase 4)

        #
        # TRACE PLAN ONCE
        #
        step_id += 1
        self.trace.add_step(
            StepTrace(
                step=step_id,
                tool="planner",
                event_type=TraceEventType.PLAN,
                args={},
                output=plan.model_dump(),
                success=True,
                latency_ms=0
            )
        )

        #
        # EXECUTE PLAN STEPS
        #
        for planned_step in plan.steps:

            print(f"[AGENT] Executing: {planned_step.tool}")

            tool_name = planned_step.tool
            args = planned_step.args or {}

            # ----------------------------
            # FIX 4: INPUT GUARDRAIL (stub)
            # ----------------------------
            if not self.guardrails.validate_tool_input(tool_name, args):
                self._trace_failed(tool_name, args, "Blocked by guardrail")
                failed_tools.add(tool_name)
                continue

            #
            # invalid tool
            #
            if tool_name not in self.tools.list_tools():
                self._trace_failed(tool_name, args, "Invalid tool")
                continue

            #
            # already failed
            #
            if tool_name in failed_tools:

                step_id += 1
                self.trace.add_step(
                    StepTrace(
                        step=step_id,
                        tool=tool_name,
                        event_type=TraceEventType.TOOL_SKIPPED,
                        args=args,
                        output="Previously failed",
                        success=False,
                        latency_ms=0
                    )
                )
                continue

            #
            # EXECUTE TOOL
            #
            start = time.time()

            output = self._execute(tool_name, args)

            latency_ms = int((time.time() - start) * 1000)

            # ----------------------------
            # FIX 4: OUTPUT GUARDRAIL (stub)
            # ----------------------------
            output = self.guardrails.validate_tool_output(tool_name, output)

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

            state.observations.append(f"[{tool_name}] {output}")

            step_id += 1

            self.trace.add_step(
                StepTrace(
                    step=step_id,
                    tool=tool_name,
                    event_type=(
                        TraceEventType.TOOL_EXECUTION
                        if success
                        else TraceEventType.TOOL_FAILED
                    ),
                    args=args,
                    output=str(output),
                    success=success,
                    latency_ms=latency_ms
                )
            )

            if not success:
                failed_tools.add(tool_name)

        #
        # FINAL ANSWER
        #
        final_answer = self._final_answer(state, tool_results)

        # ----------------------------
        # FIX 3: TRACE FINAL ANSWER
        # ----------------------------
        step_id += 1
        self.trace.add_step(
            StepTrace(
                step=step_id,
                tool="final_answer",
                event_type=TraceEventType.FINAL_ANSWER,
                args={},
                output=final_answer,
                success=True,
                latency_ms=0
            )
        )

        return self._build_response(state, final_answer)
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

Your job is to decide EXACTLY ONE next action.

==================================================
CRITICAL OUTPUT RULES
==================================================

You MUST return EXACTLY ONE valid JSON object.

You MUST NOT return:
- multiple JSON objects
- explanations
- markdown
- code fences
- text outside JSON

ONLY ONE JSON OBJECT IS ALLOWED.

==================================================
VALID OUTPUT FORMAT
==================================================

Tool call:

{{"tool":"get_time","args":{{}}}}

{{"tool":"search_docs","args":{{"query":"pytorch"}}}}

Final answer:

{{"final":true,"answer":"..."}}

==================================================
INVALID OUTPUTS
==================================================

❌ Multiple JSON objects:

{{"tool":"get_time","args":{{}}}}
{{"tool":"search_docs","args":{{}}}}

❌ Text + JSON:

Tool: get_time

{{"tool":"get_time","args":{{}}}}

❌ Explanations before JSON:

I will now call a tool:

{{"tool":"get_time","args":{{}}}}

==================================================
HARD RULES
==================================================

- Return ONLY ONE JSON object
- No multiple actions in one response
- No commentary or reasoning
- NEVER retry a failed tool
- NEVER repeat the previous tool
- NEVER assume a tool succeeded without observing output
- When calling search_docs, use search terms from the USER REQUEST.
- Do NOT invent search queries.
- Do NOT replace tensorflow with pytorch.
- Extract arguments directly from the request.

If unsure:
→ choose the most appropriate next tool

If all tasks are complete or failed:
→ return final=true

==================================================
FAILED TOOLS
==================================================

{failed_summary}

==================================================
TOOL RESULTS
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
OUTPUT RULE
==================================================

Return ONLY a JSON object.
"""
        validator = StructuredOutputValidator()
        MAX_JSON_RETRIES = 2
        for attempt in range(MAX_JSON_RETRIES):
            raw = self.model.generate(prompt)

            # Fixed — observability logging moved inside except block
            try:
                data = validator.safe_parse(raw)

                if "tool" in data:
                    return ToolAction(**data).dict()

                if "final" in data:
                    return FinalAnswer(**data).dict()

                raise StructuredOutputError("Unknown output format")

            except StructuredOutputError as e:
                print("[AGENT] Structured output failure:", str(e))
                print("[OBSERVABILITY] structured_output_failure", {
                    "raw": raw,
                    "error": str(e)
                })
                return {
                    "final": True,
                    "answer": "System failed to produce valid structured output."
                }


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

        start = time.time()

        answer = self.model.generate(prompt)

        latency_ms = int((time.time() - start) * 1000)

        self.trace.add_step(
            StepTrace(
                step=len(self.trace.steps) + 1,
                tool="final_answer",
                event_type=TraceEventType.FINAL_ANSWER,
                args={},
                output=answer,
                success=True,
                latency_ms=latency_ms
            )
        )

        return answer

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
    
    def _build_response(self, state, answer):
        return {
            "answer": answer,
            "trace": self.trace.to_dict()
        }