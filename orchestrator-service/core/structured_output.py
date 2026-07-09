import json
from typing import Any, Dict, Type, Callable


class StructuredOutputError(Exception):
    pass


class StructuredOutputValidator:

    def __init__(self):
        pass

    def parse_json(self, text: str) -> Dict[str, Any]:
        """
        Strict JSON extraction from LLM output.
        """
        if not text:
            raise StructuredOutputError("Empty response")

        text = text.strip()

        # remove markdown fences
        text = text.replace("```json", "").replace("```", "")

        try:
            return json.loads(text)
        except Exception as e:
            raise StructuredOutputError(f"Invalid JSON: {str(e)}")

    def validate_schema(self, data: dict, schema_validator: Callable) -> dict:
        """
        schema_validator = pydantic model OR custom validator
        """
        try:
            return schema_validator(**data)
        except Exception as e:
            raise StructuredOutputError(f"Schema validation failed: {str(e)}")

    def safe_parse(self, text: str, schema_validator: Callable = None):
        """
        Full pipeline: parse + validate
        """
        data = self.parse_json(text)

        if schema_validator:
            return self.validate_schema(data, schema_validator)

        return data
