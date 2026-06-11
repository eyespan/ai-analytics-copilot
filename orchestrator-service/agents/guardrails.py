# agents/guardrails.py

import re
from typing import Any, Dict
from schemas.tool_schemas import TOOL_SCHEMAS
from config.permissions import TOOL_PERMISSIONS


class Guardrails:

    def __init__(self):

        # simple injection patterns (extend later)
        self.block_patterns = [

            r"ignore previous instructions",

            r"reveal system prompt",

            r"show hidden prompt",

            r"jailbreak",

            r"developer instructions",

            r"drop all rules",

            r"bypass guardrails"
        ]

    #
    #  #INPUT GUARDRAIL (validator): block certain patterns in tool inputs (e.g. jailbreak attempts, prompt injection)
    #
    def validate_tool_input(
        self,
        tool_name: str,
        args: dict
    ) -> bool:

        schema = TOOL_SCHEMAS.get(tool_name)

        #
        # unknown tool schema
        #
        if schema is None:
            return False

        #
        # check required args
        #
        for field_name, field_type in schema.items():

            if field_name not in args:
                print(
                    f"[GUARDRAIL] Missing required arg "
                    f"{field_name} for {tool_name}"
                )
                return False

            if not isinstance(args[field_name], field_type):
                print(
                    f"[GUARDRAIL] Invalid type for "
                    f"{field_name}"
                )
                return False

        #
        # reject unexpected args
        #
        for field_name in args:

            if field_name not in schema:
                print(
                    f"[GUARDRAIL] Unexpected arg "
                    f"{field_name} for {tool_name}"
                )
                return False

        return True

    #
    # OUTPUT GUARDRAIL
            
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
    
   
    
    #output guardrail (sanitizer): block certain patterns in tool outputs (e.g. sensitive info, secrets)
      
    def validate_tool_output(
        self,
        tool_name,
        output
    ):

        text = str(output).lower()

        #
        # prompt injection leakage
        #
        for pattern in self.block_patterns:

            if re.search(pattern, text):
                return "[BLOCKED_BY_GUARDRAIL]"

        #
        # secrets
        #
        blocked = [

            "api_key",
            "secret",
            "password",
            "token"
        ]

        for word in blocked:

            if word in text:
                return "[BLOCKED_BY_GUARDRAIL]"

        return output
    
    # validdate plan
    def validate_plan(self, plan) -> bool:

        try:
            if plan is None:
                return False

            if not hasattr(plan, "steps"):
                return False

            if not isinstance(plan.steps, list):
                return False

            if len(plan.steps) == 0:
                return False
            
            ALLOWED_TOOLS = set(
                        TOOL_SCHEMAS.keys()
            )

            for step in plan.steps:

                if not step.tool:
                    return False

                if not isinstance(step.args, dict):
                    return False
                
                if step.tool not in ALLOWED_TOOLS:
                     return False
                
                if not self.validate_tool_input(
                    step.tool,
                    step.args
                ):
                    return False

            return True

        except Exception:
            return False
        


    def validate_prompt(self, query: str) -> bool:
        """
        Detect prompt injection / system override attempts.
        """

        if not query:
            return False

        q = query.lower()

        # -------------------------
        # injection patterns
        # -------------------------
        injection_patterns = [
            r"ignore (all|previous) instructions",
            r"reveal (system|hidden) prompt",
            r"system prompt",
            r"developer instructions",
            r"you are now",
            r"act as",
            r"jailbreak",
            r"bypass (all|any) (rules|guardrails|filters)",
            r"drop all rules",
            r"pretend you are",
            r"override",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, q):
                print(f"[GUARDRAIL] Prompt injection detected: {pattern}")
                return False

        # -------------------------
        # tool manipulation attempts
        # -------------------------
        tool_override_keywords = [
            "use tool",
            "call system tool",
            "force tool",
            "execute hidden tool"
        ]

        for k in tool_override_keywords:
            if k in q:
                print(f"[GUARDRAIL] Tool override attempt detected: {k}")
                return False

        return True
        
    def tool_exists(self, tool_name):
        return tool_name in TOOL_SCHEMAS