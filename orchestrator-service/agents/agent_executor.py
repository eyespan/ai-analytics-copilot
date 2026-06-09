import json
import re
from typing import Dict, Any

from agents.state import AgentState


class AgentExecutor:

    def __init__(self, model, tool_registry, max_steps: int = 5):
        self.model = model
        self.tools = tool_registry
        self.max_steps = max_steps

    # =========================
    # ENTRYPOINT
    # =========================
    def run(self, query: str, context: str = "") -> str:

        state = AgentState(query=query)

        for step_idx in range(self.max_steps):

            print(f"[AGENT] Step {step_idx + 1}")

            action = self._think(state, context)

            print(f"[AGENT] Action: {action}")

            # -------------------------
            # FINAL ANSWER
            # -------------------------
            if action.get("final"):
                print("[AGENT] Final answer generated")
                return action.get("answer", "No answer generated")

            tool_name = action.get("tool")
            args = action.get("args", {}) or {}

            # -------------------------
            # TOOL VALIDATION FIRST (IMPORTANT FIX)
            # -------------------------
            if not tool_name:
                state.observations.append("No tool selected by model.")
                continue

            if tool_name not in self.tools.list_tools():
                obs = f"Invalid tool: {tool_name}"
                state.observations.append(obs)
                continue

            # -------------------------
            # LOOP GUARD (FIXED ORDER)
            # -------------------------
            if (
                state.last_tool is not None
                and tool_name == state.last_tool
                and args == state.last_args
            ):
                print("[AGENT] Repeated tool call detected → stopping early")
                return self._final_answer(state)

            # -------------------------
            # EXECUTE TOOL
            # -------------------------
            observation = self._execute(tool_name, args)
            print(f"[AGENT] Observation stored: {observation}")

            state.observations.append(
                f"[{tool_name}] {observation}"
            )

            # -------------------------
            # UPDATE STATE AFTER EXECUTION (CRITICAL FIX)
            # -------------------------
            state.last_tool = tool_name
            state.last_args = args

            # -------------------------
            # SAFETY LIMIT
            # -------------------------
            if len(state.observations) > 20:
                print("[AGENT] Observation limit reached")
                break

        print("[AGENT] Max steps reached → synthesizing answer")
        return self._final_answer(state)
    
# =========================
# THINK STEP
# =========================
    def _think(self, state: AgentState, context: str) -> Dict[str, Any]:

        step_number = len(state.observations) + 1

        # -------------------------
        # TASK STATE DERIVATION (FIX #3 CORE IDEA)
        # -------------------------
        obs_text = " ".join(state.observations).lower()

        task_status = {
            "get_time": any("[get_time]" in o for o in state.observations),
            "search_docs": any(
                "[search_docs]" in o or "[search]" in o
                for o in state.observations
             ),
            "summarize": "summary" in obs_text or "final" in obs_text
        }

        has_time = task_status["get_time"]
        has_search = task_status["search_docs"]

        if has_time and has_search and not task_status["summarize"]:
            # force final summarization step
            pass

        prompt = f"""
    You are an AI planning agent.

    Your job is to decide EXACTLY ONE next action.

    ==================================================
    IMPORTANT RULES
    ==================================================

    1. Do NOT repeat completed tasks.
    2. Use TASK STATUS below to decide what is done.
    3. Execute ONLY ONE tool per step.
    4. If everything is done → return final=true.
    5. Output ONLY valid JSON.

    ==================================================
    TASK STATUS (AUTO-DETECTED)
    ==================================================

    - get_time: {task_status["get_time"]}
    - search_docs: {task_status["search_docs"]}
    - summarize: {task_status["summarize"]}

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
    OBSERVATIONS
    ==================================================

    {state.observations}

    ==================================================
    STOP CONDITION
    ==================================================

    If all required tasks are complete:
    return:
    {{
    "final": true,
    "answer": "..."
    }}

    ==================================================
    OUTPUT FORMAT
    ==================================================

    If calling tool:
    {{
    "tool": "tool_name",
    "args": {{}}
    }}

    If finished:
    {{
    "final": true,
    "answer": "..."
    }}
    """

        raw = self.model.generate(prompt)

        print("========== AGENT PROMPT ==========")
        print(prompt)
        print("==================================")
        print(f"[AGENT] Raw model output: {raw}")

        cleaned = self._clean_json(raw)

        try:
            return json.loads(cleaned)
        except Exception:
            return {
                "final": True,
                "answer": cleaned
            }
    # =========================
    # TOOL EXECUTION
    # =========================
    def _execute(self, tool_name: str, args: Dict[str, Any]):

        print(f"[AGENT] Executing tool: {tool_name}")
        print(f"[AGENT] Tool args: {args}")

        tool = self.tools.get(tool_name)

        if not tool:
            print(f"[AGENT] Tool not found: {tool_name}")
            return f"Tool not found: {tool_name}"

        try:
            result = tool(args)
            print(f"[AGENT] Tool result: {result}")
            return result
        except Exception as e:
            print(f"[AGENT] Tool execution error: {str(e)}")
            return f"Tool execution error: {str(e)}"

    # =========================
    # FINAL SYNTHESIS
    # =========================
    def _final_answer(self, state: AgentState):

        prompt = f"""
You are a reasoning assistant.

Create a final answer based ONLY on observations.

USER QUERY:
{state.query}

OBSERVATIONS:
{state.observations}

RULE:
- Do not hallucinate new tools or data
- Use only observations above
"""

        return self.model.generate(prompt)

    # =========================
    # JSON CLEANER (IMPORTANT FIX)
    # =========================
    def _clean_json(self, text: str) -> str:
        """
        Removes markdown and extracts JSON safely.
        """

        if not text:
            return "{}"

        # remove code block wrappers
        text = text.strip()
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)

        # extract first JSON object if model adds noise
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)

        return text