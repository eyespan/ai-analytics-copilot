# agents/guardrails.py

import re
from typing import Dict, Any, List

from schemas.tool_schemas import TOOL_SCHEMAS
from config.permissions import TOOL_PERMISSIONS


class Guardrails:

    # ---------------------------------------------------------
    # PRODUCTION LIMITS
    # ---------------------------------------------------------
    MAX_TOOL_CALLS = 10
    MAX_PLAN_STEPS = 10

    def __init__(self):
        # -----------------------------------------------------
        # AUDIT EVENTS
        # -----------------------------------------------------
        self.events: List[Dict[str, Any]] = []

        # -----------------------------------------------------
        # PROMPT INJECTION PATTERNS
        # -----------------------------------------------------
        self.block_patterns = [

            r"ignore previous instructions",
            r"reveal system prompt",
            r"show hidden prompt",
            r"jailbreak",
            r"developer instructions",
            r"drop all rules",
            r"bypass guardrails"
        ]

        # -----------------------------------------------------
        # SENSITIVE DATA PATTERNS
        # -----------------------------------------------------
        self.sensitive_patterns = [

            # AWS access keys
            r"AKIA[0-9A-Z]{16}",

            # OpenAI-style keys
            r"sk-[A-Za-z0-9]{20,}",

            # Bearer tokens
            r"Bearer\s+[A-Za-z0-9\-\._]+",

            # JWT
            r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+",

            # SSN
            r"\b\d{3}-\d{2}-\d{4}\b",

            # Credit cards
            r"\b(?:\d[ -]*?){13,16}\b"
        ]

        self.max_tool_calls = 10   # 🔥 NEW: execution safety limit

    # =========================================================
    # AUDIT EVENTS
    # =========================================================
    def record_event(
        self,
        event_type: str,
        details: Dict[str, Any]
    ):
        self.events.append({
            "event": event_type,
            "details": details
        })

    def get_events(self):
        return self.events

    # =========================================================
    # TOOL EXECUTION LIMITS
    # =========================================================
    def validate_tool_limit(
        self,
        current_step: int
    ) -> bool:

        if current_step > self.MAX_TOOL_CALLS:

            self.record_event(
                "tool_limit_exceeded",
                {
                    "step": current_step
                }
            )

            return False

        return True

    # =========================================================
    # PLAN SIZE VALIDATION
    # =========================================================
    def validate_plan_size(
        self,
        plan
    ) -> bool:

        if not hasattr(plan, "steps"):
            return False

        if len(plan.steps) > self.MAX_PLAN_STEPS:

            self.record_event(
                "plan_too_large",
                {
                    "steps": len(plan.steps)
                }
            )

            return False

        return True

    # =========================================================
    # SENSITIVE DATA DETECTION
    # =========================================================
    def contains_sensitive_data(
        self,
        text: str
    ) -> bool:

        if not text:
            return False

        for pattern in self.sensitive_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False

    # =========================================================
    # TOOL INPUT VALIDATION
    # =========================================================
    def validate_tool_input(
        self,
        tool_name: str,
        args: dict
    ) -> bool:

        schema = TOOL_SCHEMAS.get(tool_name)

        if schema is None:

            self.record_event(
                "invalid_tool_schema",
                {
                    "tool": tool_name
                }
            )

            return False

        for field_name, field_type in schema.items():

            if field_name not in args:

                self.record_event(
                    "missing_argument",
                    {
                        "tool": tool_name,
                        "field": field_name
                    }
                )

                return False

            if not isinstance(
                args[field_name],
                field_type
            ):

                self.record_event(
                    "invalid_argument_type",
                    {
                        "tool": tool_name,
                        "field": field_name
                    }
                )

                return False

        for field_name in args:

            if field_name not in schema:

                self.record_event(
                    "unexpected_argument",
                    {
                        "tool": tool_name,
                        "field": field_name
                    }
                )

                return False

        return True

    # =========================================================
    # TOOL OUTPUT SCHEMA VALIDATION
    # =========================================================
    def validate_tool_schema(
        self,
        tool_name: str,
        args: dict
    ) -> bool:

        if tool_name not in TOOL_SCHEMAS:
            return False

        schema = TOOL_SCHEMAS[tool_name]

        for field, field_type in schema.items():

            if field not in args:
                return False

            if not isinstance(args[field], field_type):
                return False

        return True

    # =========================================================
    # TOOL PERMISSIONS
    # =========================================================
    def validate_tool_permission(
        self,
        tool_name: str,
        role: str = "agent"
    ) -> bool:

        allowed = TOOL_PERMISSIONS.get(
            tool_name,
            []
        )

        return role in allowed

    # =========================================================
    # TOOL OUTPUT GUARDRAIL
    # =========================================================
    def validate_tool_output(
        self,
        tool_name,
        output
    ):

        text = str(output)

        # ----------------------------
        # prompt leakage
        # ----------------------------
        for pattern in self.block_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):

                self.record_event(
                    "output_blocked_prompt_leak",
                    {
                        "tool": tool_name
                    }
                )

                return "[BLOCKED_BY_GUARDRAIL]"

        # ----------------------------
        # secret detection
        # ----------------------------
        if self.contains_sensitive_data(text):

            self.record_event(
                "output_blocked_sensitive_data",
                {
                    "tool": tool_name
                }
            )

            return "[BLOCKED_BY_GUARDRAIL]"

        blocked = [
            "api_key",
            "secret",
            "password",
            "token"
        ]

        lower_text = text.lower()

        for word in blocked:

            if word in lower_text:

                self.record_event(
                    "output_blocked_secret_keyword",
                    {
                        "tool": tool_name,
                        "keyword": word
                    }
                )

                return "[BLOCKED_BY_GUARDRAIL]"

        return output

    # =========================================================
    # PLAN VALIDATION
    # =========================================================
    def validate_plan(
        self,
        plan
    ) -> bool:

        try:

            if plan is None:
                return False

            if not hasattr(plan, "steps"):
                return False

            if not isinstance(plan.steps, list):
                return False

            if len(plan.steps) == 0:
                return False

            if not self.validate_plan_size(plan):
                return False

            allowed_tools = set(
                TOOL_SCHEMAS.keys()
            )

            for step in plan.steps:

                if not step.tool:
                    return False

                if not isinstance(
                    step.args,
                    dict
                ):
                    return False

                if step.tool not in allowed_tools:
                    return False

                if not self.validate_tool_input(
                    step.tool,
                    step.args
                ):
                    return False

            return True

        except Exception:
            return False

    # =========================================================
    # PROMPT RISK SCORING
    # =========================================================
    def score_prompt_risk(
        self,
        query: str
    ) -> Dict[str, Any]:

        q = query.lower()

        score = 0
        reasons = []

        rules = {

            r"ignore (all|previous) instructions": 40,
            r"reveal (system|hidden) prompt": 40,
            r"system prompt": 30,
            r"developer instructions": 30,
            r"jailbreak": 50,
            r"override": 25,
            r"bypass": 25,
            r"act as": 20,
            r"you are now": 20
        }

        for pattern, value in rules.items():

            if re.search(pattern, q):

                score += value
                reasons.append(pattern)

        if score >= 50:
            risk = "high"
        elif score >= 20:
            risk = "medium"
        else:
            risk = "low"

        return {
            "score": score,
            "risk": risk,
            "reasons": reasons
        }

    # =========================================================
    # PROMPT VALIDATION
    # =========================================================
    def validate_prompt(
        self,
        query: str
    ) -> bool:

        if not query:
            return False

        risk = self.score_prompt_risk(query)

        if risk["risk"] == "high":

            self.record_event(
                "prompt_blocked",
                risk
            )

            return False

        tool_override_keywords = [
            "use tool",
            "call system tool",
            "force tool",
            "execute hidden tool"
        ]

        q = query.lower()

        for keyword in tool_override_keywords:

            if keyword in q:

                self.record_event(
                    "tool_override_attempt",
                    {
                        "keyword": keyword
                    }
                )

                return False

        return True

    # =========================================================
    # TOOL EXISTS
    # =========================================================
    def tool_exists(
        self,
        tool_name
    ):
        return tool_name in TOOL_SCHEMAS

    # =========================================================
    # LLM OUTPUT VALIDATION
    # =========================================================
    def validate_llm_output(
        self,
        text: str
    ) -> bool:

        q = text.lower()

        patterns = [

            "ignore previous",
            "bypass",
            "reveal system prompt",
            "call hidden tool",
            "override plan"
        ]

        return not any(
            p in q
            for p in patterns
        )