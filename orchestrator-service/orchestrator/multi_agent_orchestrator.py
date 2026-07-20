from dataclasses import dataclass

from agents.state import AgentState
from agents.trace import AgentTrace, StepTrace, TraceEventType
from workflows.workflow_manager import WorkflowManager


@dataclass
class OrchestrationResult:
    answer: str
    trace: dict
    workflow: dict


class MultiAgentOrchestrator:

    def __init__(self, planner, repair, executor, critic=None):
        self.planner = planner
        self.repair = repair
        self.executor = executor
        self.critic = critic

        self.workflow_manager = WorkflowManager()

    def run(self, query: str, context: str = "") -> dict:

        workflow = self.workflow_manager.create_workflow(query)
        workflow.start()

        state = AgentState(query=query)

        trace = AgentTrace(query=query)

        step_id = 0

        # ====================================================
        # PLANNER
        # ====================================================

        try:

            plan = self.planner.create_plan(query)

            if not plan or not getattr(plan, "steps", None):
                workflow.fail_workflow()
                return self._fail(workflow, "Empty plan")

            step_id += 1

            trace.add_step(
                StepTrace(
                    step=step_id,
                    tool="planner_agent",
                    event_type=TraceEventType.PLAN,
                    args={},
                    validated_args=None,
                    output=plan.model_dump(),
                    success=True,
                    latency_ms=0,
                )
            )

        except Exception as e:

            workflow.fail_workflow()

            return self._fail(workflow, f"Planner error: {str(e)}")

        # ====================================================
        # REPAIR
        # ====================================================

        try:

            repaired_plan = self.repair.repair(plan, query)

            step_id += 1

            trace.add_step(
                StepTrace(
                    step=step_id,
                    tool="repair_agent",
                    event_type=TraceEventType.PLAN_REPAIRED,
                    args={},
                    validated_args=None,
                    output={
                        "changed": plan.model_dump() != repaired_plan.model_dump(),
                        "plan": repaired_plan.model_dump(),
                    },
                    success=True,
                    latency_ms=0,
                )
            )

        except Exception as e:

            workflow.fail_workflow()

            return self._fail(workflow, f"Repair error: {str(e)}")

        # ====================================================
        # EXECUTION
        # ====================================================

        state.context = context

        result = self.executor.run_plan(repaired_plan, query=query, workflow=workflow, state=state)

        executor_trace = result.get("trace", {})

        if executor_trace:

            for step in executor_trace.get("steps", []):
                if isinstance(step, dict):
                    trace.steps.append(step)  # or convert properly
                else:
                    trace.steps.append(step)

        # ====================================================
        # CRITIC
        # ====================================================

        if self.critic:

            try:

                critique = self.critic.review(result)

                step_id += 1

                trace.add_step(
                    StepTrace(
                        step=step_id,
                        tool="critic_agent",
                        event_type="critique",
                        args={},
                        validated_args=None,
                        output=critique,
                        success=True,
                        latency_ms=0,
                    )
                )

                result["critique"] = critique

            except Exception as e:

                step_id += 1

                trace.add_step(
                    StepTrace(
                        step=step_id,
                        tool="critic_agent",
                        event_type="critique_failed",
                        args={},
                        validated_args=None,
                        output=str(e),
                        success=False,
                        latency_ms=0,
                    )
                )

        # ========================================================
        # WORKFLOW FINALIZATION
        # ========================================================

        if workflow.status != "failed":

            if workflow.failed_steps:
                workflow.status = "completed_with_errors"
            else:
                workflow.finish()

        return {
            "answer": result.get("answer"),
            "trace": trace.to_dict(),
            "workflow": {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status,
                "current_step": workflow.current_step,
                "completed_steps": workflow.completed_steps,
                "failed_steps": workflow.failed_steps,
            },
            "critique": result.get("critique"),
        }

    def _fail(self, workflow, msg: str):
        return {
            "answer": msg,
            "trace": {},
            "workflow": {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status,
                "current_step": workflow.current_step,
                "completed_steps": workflow.completed_steps,
                "failed_steps": workflow.failed_steps,
            },
        }
