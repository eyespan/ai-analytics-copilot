from typing import Dict, Any, Optional
import os
import json
from clients.ollama_client import OllamaClient


# =========================
# LLM PROVIDERS (ABSTRACTIONS)
# =========================

class BaseModel:
    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def stream(self, prompt: str):
        raise NotImplementedError


# -------------------------
# BEDROCK (Claude / Titan)
# -------------------------
class BedrockModel(BaseModel):
    def __init__(self, client, model_id: str):
        super().__init__(f"bedrock:{model_id}")
        self.client = client
        self.model_id = model_id

    def generate(self, prompt: str) -> str:
        response = self.client.invoke_model(
            modelId=self.model_id,
            body={"prompt": prompt}
        )
        return response["body"]

    def stream(self, prompt: str):
        return self.client.invoke_model_with_stream(
            modelId=self.model_id,
            body={"prompt": prompt}
        )


# -------------------------
# OPENAI (optional)
# -------------------------
class OpenAIModel(BaseModel):
    def __init__(self, client, model: str = "gpt-4o-mini"):
        super().__init__(f"openai:{model}")
        self.client = client
        self.model = model

    def generate(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    def stream(self, prompt: str):
        return self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )


# -------------------------
# OLLAMA (local fallback)
# -------------------------
class OllamaModel(BaseModel):
    def __init__(self, client, model: str = "qwen2.5:7b"):
        super().__init__(f"ollama:{model}")
        self.client = client
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.generate(prompt=prompt)
        if isinstance(response, dict):
            return response.get("response", "")
        return response

    def stream(self, prompt: str):
        for chunk in self.client.stream_generate(prompt=prompt):
            yield chunk

# =========================
# ROUTER (CORE LOGIC)
# =========================

class ModelRouter:
    """
    Decides which LLM to use based on:
    - query complexity
    - cost sensitivity
    - latency needs
    - environment config
    """

    def __init__(self):
        self.primary_provider = os.getenv("PRIMARY_LLM", "bedrock")
        self.fallback_provider = os.getenv("FALLBACK_LLM", "ollama")

        # injected clients (set in main app startup)
        self.bedrock_client = None
        self.openai_client = None
        self.ollama_client = OllamaClient(
            base_url=os.getenv("OLLAMA_HOST", "http://ollama:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        )

    # -------------------------
    # MODEL SELECTION
    # -------------------------
    def select_model(self, query: str, context: str = "") -> BaseModel:

        complexity = self._estimate_complexity(query, context)

        # -----------------------------------
        # HIGH COMPLEXITY → BEDROCK (Claude)
        # -----------------------------------
        if complexity == "high":
            if self.bedrock_client:
                return BedrockModel(self.bedrock_client, "anthropic.claude-3-sonnet-20240229-v1:0")

        # -----------------------------------
        # MEDIUM → OpenAI or Bedrock fallback
        # -----------------------------------
        if complexity == "medium":
            if self.openai_client:
                return OpenAIModel(self.openai_client)
            if self.bedrock_client:
                return BedrockModel(self.bedrock_client, "anthropic.claude-3-haiku-20240307-v1:0")

        # -----------------------------------
        # LOW COST → OLLAMA
        # -----------------------------------
        if self.ollama_client:
            return OllamaModel(self.ollama_client)

        # -----------------------------------
        # FINAL FALLBACK
        # -----------------------------------
        if self.bedrock_client:
            return BedrockModel(self.bedrock_client, "anthropic.claude-3-haiku-20240307-v1:0")

        raise Exception("No LLM provider available")

    # -------------------------
    # SIMPLE QUERY CLASSIFIER
    # -------------------------
    def _estimate_complexity(self, query: str, context: str) -> str:

        q = query.lower()

        # heuristics (we can upgrade later with ML classifier)
        long_query = len(q.split()) > 12
        has_reasoning_words = any(word in q for word in [
            "explain", "compare", "why", "how", "architecture", "design"
        ])

        has_multiple_intents = " and " in q or " vs " in q

        if long_query or has_multiple_intents or has_reasoning_words:
            return "high"

        if len(q.split()) > 6:
            return "medium"

        return "low"