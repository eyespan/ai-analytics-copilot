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
from agents.guardrails import Guardrails  # Ensure Guardrails is defined in agents.guardrails module
from agents.plan_repair import PlanRepairEngine
from workflows.workflow_manager import WorkflowManager





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
        self.guardrails = Guardrails()
        self.plan_repair = PlanRepairEngine()
        self.workflow_manager = WorkflowManager()
        

    # ------------------------------------------------------------
    # MAIN RUN LOOP
    # ------------------------------------------------------------
   
    def run(self, query: str, context: str = ""):

        state = AgentState(query=query)
        workflow = self.workflow_manager.create_workflow(query)
        workflow.start()
        self.trace = AgentTrace(query=query)

        tool_results: Dict[str, ToolResult] = {}
        failed_tools: Set[str] = set()

        step_id = 0

        # --------------------------------------------------------
        # GUARDRAIL: PROMPT INJECTION
        # --------------------------------------------------------
        if not self.guardrails.validate_prompt(query):
            return self._fallback_answer("Blocked by prompt guardrail")

        # --------------------------------------------------------
        # CREATE EXECUTION PLAN
        # --------------------------------------------------------
        planner = Planner(self.model)

        try:
            original_plan = planner.create_plan(query)

            if not original_plan or not getattr(original_plan, "steps", None):
                return self._fallback_answer("Empty plan from planner")

            step_id += 1
            self.trace.add_step(
                StepTrace(
                    step=step_id,
                    tool="planner",
                    event_type=TraceEventType.PLAN,
                    args={},
                    output=original_plan.model_dump(),
                    success=True,
                    latency_ms=0
                )
            )

            plan = self.plan_repair.repair(original_plan, query)

            if not plan or not getattr(plan, "steps", None):
                return self._fallback_answer("Empty plan after repair")

            step_id += 1
            self.trace.add_step(
                StepTrace(
                    step=step_id,
                    tool="plan_repair",
                    event_type=TraceEventType.PLAN_REPAIRED,
                    args={},
                    output={
                        "changed": original_plan.model_dump() != plan.model_dump(),
                        "plan": plan.model_dump()
                    },
                    success=True,
                    latency_ms=0
                )
            )

        except Exception as e:
            return self._fallback_answer(f"Planner error: {str(e)}")

        # --------------------------------------------------------
        # PLAN VALIDATION
        # --------------------------------------------------------
        if not self.guardrails.validate_plan(plan):
            return self._fallback_answer("Invalid plan blocked by guardrails")

        # --------------------------------------------------------
        # EXECUTE PLAN (FIXED LOOP)
        # --------------------------------------------------------
        for planned_step in plan.steps:

            tool_name = planned_step.tool
            args = planned_step.args or {}

           
            print(f"[AGENT] Executing: {tool_name}")

            # ----------------------------
            # TOOL EXISTS CHECK
            # ----------------------------
            if tool_name not in self.tools.list_tools():
                self._trace_failed(tool_name, args, "Invalid tool")
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)
                continue

            # ----------------------------
            # PERMISSION CHECK
            # ----------------------------
            if not self.guardrails.validate_tool_permission(tool_name):
                self._trace_failed(tool_name, args, "Permission denied")
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)
                continue

            # ----------------------------
            # INPUT VALIDATION
            # ----------------------------
            if not self.guardrails.validate_tool_input(tool_name, args):
                self._trace_failed(tool_name, args, "Input blocked by guardrail")
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)
                continue

            # ----------------------------
            # EXECUTION
            # ----------------------------
            start = time.time()
            
            input_model = self.tools.get_input_model(
                tool_name
            )
            if input_model:

                try:

                    validated_args = input_model(
                            **args
                        ).model_dump()

                except Exception as e:

                    workflow.fail_step(tool_name)

                    step_id += 1

                    self.trace.add_step(
                        StepTrace(
                            step=step_id,
                            tool=tool_name,
                            event_type=TraceEventType.SCHEMA_VALIDATION_FAILED,
                            args=args,
                            validated_args=validated_args,
                            output=str(e),
                            success=False,
                            latency_ms=0
                        )
                    )

                    continue
            else:
                validated_args = None


            output = self._execute(
                tool_name,
                validated_args
            )

            output_model = self.tools.get_output_model(tool_name)

            #if isinstance(output, str):
                # normalize scalar → dict if schema exists
            #    output_model = self.tools.get_output_model(tool_name)


            #if not isinstance(output, dict):
            #    raise ValueError(
            #        f"Tool {tool_name} must return dict, got {type(output)}"
            #    )

            if output_model:

                try:
                    if not isinstance(output, dict):
                      raise ValueError("Tool output must be dict before validation")
                    
                    validated_output = output_model(
                        **output
                    ).model_dump()

                    output = validated_output

                except Exception as e:

                    workflow.fail_step(tool_name)

                    step_id += 1

                    self.trace.add_step(
                        StepTrace(
                            step=step_id,
                            tool=tool_name,
                            event_type=TraceEventType.SCHEMA_VALIDATION_FAILED,
                            args=args,
                            validated_args=validated_args,
                            output=f"Output schema error: {str(e)}",
                            success=False,
                            latency_ms=0
                        )
                    )

                    continue




            latency_ms = int((time.time() - start) * 1000)

            output = self.guardrails.validate_tool_output(tool_name, output)

            success = not any(
                str(output).startswith(prefix)
                for prefix in (
                    "[DOC_ERROR]",
                    "Tool execution error",
                    "Tool not found"
                )
            )

            if success:
                workflow.complete_step(tool_name)
            else:
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)

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
                    event_type=TraceEventType.TOOL_EXECUTION if success else TraceEventType.TOOL_FAILED,
                    args=args,
                    validated_args=validated_args,
                    output=output,
                    success=success,
                    latency_ms=latency_ms
                )
            )

        # --------------------------------------------------------
        # FINAL ANSWER
        # --------------------------------------------------------
        final_answer = self._final_answer(state, tool_results)

        if workflow.failed_steps:
            workflow.status = "completed_with_errors"
        else:
            workflow.finish()

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

        response = self._build_response(state, final_answer)

        response["workflow"] = {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "completed_steps": workflow.completed_steps,
            "failed_steps": workflow.failed_steps
        }

        return response
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

            return result

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

        #self.trace.add_step(
        #    StepTrace(
        #        step=len(self.trace.steps) + 1,
        #        tool="final_answer",
        #        event_type=TraceEventType.FINAL_ANSWER,
        #        args={},
        #        output=answer,
        #        success=True,
        #        latency_ms=latency_ms
        #    )
        #)

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

    # ------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------
    def _trace_failed(self, tool_name, args, reason):
        self.trace.add_step(
            StepTrace(
                step=len(self.trace.steps) + 1,
                tool=tool_name,
                event_type=TraceEventType.TOOL_FAILED,
                args=args,
                output=reason,
                success=False,
                latency_ms=0
            )
        )

    def _fallback_answer(self, msg: str):
        return {
            "answer": msg,
            "trace": self.trace.to_dict()
        }