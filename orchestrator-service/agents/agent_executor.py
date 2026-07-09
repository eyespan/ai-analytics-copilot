import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

# from core.structured_output import StructuredOutputValidator, StructuredOutputError
# from schemas.llm_schemas import ToolAction, FinalAnswer
from agents.guardrails import Guardrails
from agents.plan_repair import PlanRepairEngine  # optional fallback only
from agents.state import AgentState
from agents.trace import AgentTrace, StepTrace, TraceEventType
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
        self.workflow_manager = WorkflowManager()
        self.plan_repair = PlanRepairEngine()  # kept for fallback/debug only

    # ============================================================
    # OPTION B ENTRY POINT (MAIN)
    # ============================================================
    def run_plan(
        self, plan, query: str, workflow=None, state: Optional[AgentState] = None
    ):

        state = state or AgentState(query=query)

        if workflow is None:
            workflow = self.workflow_manager.create_workflow(query)
            workflow.start()

        self.trace = AgentTrace(query=query)

        tool_results: Dict[str, ToolResult] = {}
        failed_tools: Set[str] = set()

        step_id = 0

        # ========================================================
        # 🔥 NEW: TOOL EXECUTION BUDGET
        # ========================================================
        max_calls = getattr(self.guardrails, "max_tool_calls", 10)
        tool_call_count = 0

        # ========================================================
        # EXECUTE PLAN
        # ========================================================
        for planned_step in plan.steps:

            tool_name = planned_step.tool
            args = planned_step.args or {}

            print(f"[AGENT] Executing: {tool_name}")

            # ----------------------------------------------------
            # 🔥 TOOL LIMIT CHECK (HARD STOP)
            # ----------------------------------------------------
            if tool_call_count >= max_calls:
                step_id += 1

                self.trace.add_step(
                    StepTrace(
                        step=step_id,
                        tool="guardrail",
                        event_type=TraceEventType.TOOL_FAILED,
                        args={},
                        output="Tool execution limit exceeded",
                        success=False,
                        latency_ms=0,
                    )
                )

                workflow.fail_step("tool_limit")
                break

            # ----------------------------
            # TOOL EXISTS
            # ----------------------------
            step_id += 1
            if tool_name not in self.tools.list_tools():
                self._trace_failed(tool_name, args, "Invalid tool", step_id)
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)
                continue

            # ----------------------------
            # PERMISSION CHECK
            # ----------------------------
            if not self.guardrails.validate_tool_permission(tool_name):
                self._trace_failed(tool_name, args, "Permission denied", step_id)
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)
                continue

            # ----------------------------
            # INPUT GUARDRAILS
            # ----------------------------
            if not self.guardrails.validate_tool_input(tool_name, args):
                self._trace_failed(tool_name, args, "Input blocked", step_id)
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)
                continue

            # ----------------------------
            # INPUT SCHEMA VALIDATION
            # ----------------------------
            validated_args = args
            input_model = self.tools.get_input_model(tool_name)

            if input_model:
                try:
                    validated_args = input_model(**args).model_dump()
                except Exception as e:
                    step_id += 1
                    workflow.fail_step(tool_name)

                    self.trace.add_step(
                        StepTrace(
                            step=step_id,
                            tool=tool_name,
                            event_type=TraceEventType.SCHEMA_VALIDATION_FAILED,
                            args=args,
                            output=str(e),
                            success=False,
                            latency_ms=0,
                        )
                    )
                    continue

            # ----------------------------
            # EXECUTION
            # ----------------------------
            start = time.time()

            output = self._execute(tool_name, validated_args)

            output = self.guardrails.validate_tool_output(tool_name, output)

            # 🔥 COUNT ONLY AFTER REAL EXECUTION
            tool_call_count += 1

            # ----------------------------
            # OUTPUT SCHEMA VALIDATION
            # ----------------------------
            output_model = self.tools.get_output_model(tool_name)

            if output_model:
                try:
                    if not isinstance(output, dict):
                        raise ValueError("Tool output must be dict")

                    output = output_model(**output).model_dump()

                except Exception as e:
                    step_id += 1
                    workflow.fail_step(tool_name)

                    self.trace.add_step(
                        StepTrace(
                            step=step_id,
                            tool=tool_name,
                            event_type=TraceEventType.SCHEMA_VALIDATION_FAILED,
                            args=validated_args,
                            output=f"Output schema error: {str(e)}",
                            success=False,
                            latency_ms=0,
                        )
                    )
                    continue

            latency_ms = int((time.time() - start) * 1000)

            # ----------------------------
            # SUCCESS/FAIL STATUS
            # ----------------------------
            success = not str(output).startswith(
                ("Tool execution error", "Tool not found", "[DOC_ERROR]")
            )

            if success:
                workflow.complete_step(tool_name)
            else:
                workflow.fail_step(tool_name)
                failed_tools.add(tool_name)

            tool_results[tool_name] = ToolResult(
                tool=tool_name, args=validated_args, output=str(output), success=success
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
                    args=validated_args,
                    output=output,
                    success=success,
                    latency_ms=latency_ms,
                )
            )

        # ========================================================
        # FINAL ANSWER
        # ========================================================
        final_answer = self._final_answer(state, tool_results)

        step_id += 1
        self.trace.add_step(
            StepTrace(
                step=step_id,
                tool="final_answer",
                event_type=TraceEventType.FINAL_ANSWER,
                args={},
                output=final_answer,
                success=True,
                latency_ms=0,
            )
        )

        return {
            "answer": final_answer,
            "trace": self.trace.to_dict(),
            "workflow": {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status,
                "current_step": workflow.current_step,
                "completed_steps": workflow.completed_steps,
                "failed_steps": workflow.failed_steps,
            },
        }

    # ============================================================
    # LEGACY SUPPORT (OPTIONAL)
    # ============================================================
    def run(self, query: str, context: str = ""):
        raise NotImplementedError("Use MultiAgentOrchestrator.run()")

    # ============================================================
    # TOOL EXECUTION
    # ============================================================
    def _execute(self, tool_name: str, args: Dict[str, Any]):

        tool = self.tools.get(tool_name)

        if not tool:
            return f"Tool not found: {tool_name}"

        try:
            return tool(args)
        except Exception as e:
            return f"Tool execution error: {str(e)}"

    # ============================================================
    # FINAL ANSWER GENERATION
    # ============================================================
    def _final_answer(self, state: AgentState, tool_results: Dict[str, ToolResult]):

        resolved = "\n".join(f"{k}: {v.output}" for k, v in tool_results.items())

        prompt = f"""
USER: {state.query}

RETRIEVED CONTEXT:
{getattr(state, "context", "")}

TOOLS:
{resolved}

Answer using both retrieved context and tool outputs.
Be precise and factual.
"""

        return self.model.generate(prompt)

    # ============================================================
    # TRACE HELPERS
    # ============================================================
    def _trace_failed(self, tool_name, args, reason, step_id):
        self.trace.add_step(
            StepTrace(
                step=step_id,
                tool=tool_name,
                event_type=TraceEventType.TOOL_FAILED,
                args=args,
                output=reason,
                success=False,
                latency_ms=0,
            )
        )
