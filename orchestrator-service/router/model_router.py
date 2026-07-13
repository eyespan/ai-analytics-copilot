import os
from typing import Generator, Optional

from clients.bedrock_client import BedrockClient
from clients.ollama_client import OllamaClient
from config.settings import *


class BaseModel:

    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def stream(self, prompt: str):
        raise NotImplementedError


class BedrockModel(BaseModel):

    def __init__(self, client, model_id: str):
        super().__init__(f"bedrock:{model_id}")

        self.client = client
        self.model_id = model_id

    def generate(self, prompt: str) -> str:

        return self.client.generate(prompt)

    def stream(self, prompt: str):

        yield from self.client.stream_generate(prompt)


class OpenAIModel(BaseModel):
    def __init__(self, client, model: str = "gpt-4o-mini"):
        super().__init__(f"openai:{model}")
        self.client = client
        self.model = model

    def generate(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    def stream(self, prompt: str) -> Generator[str, None, None]:
        # OpenAI SDK stream returns delta objects — unwrap to strings here
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in resp:
            if text := chunk.choices[0].delta.content or "":
                yield text


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

    def stream(self, prompt: str) -> Generator[str, None, None]:
        for chunk in self.client.stream_generate(prompt=prompt):
            yield chunk


class ModelRouter:
    def __init__(self):
        self.bedrock_client = None
        self.openai_client = None
        self.ollama_client = OllamaClient(
            base_url=os.getenv("OLLAMA_HOST", "http://ollama:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        )

        self.bedrock_client = None

        if os.getenv("BEDROCK_ENABLED", "true") == "true":
            self.bedrock_client = BedrockClient(
                model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
            )

    def select_model(self, query: str, context: str = "") -> BaseModel:

        complexity = self._estimate_complexity(query, context)

        print(f"[ROUTER] complexity={complexity} query={query[:60]}")

        # ------------------------------
        # 1. HIGH complexity → Bedrock FIRST
        # ------------------------------
        if complexity == "high" and self.bedrock_client:
            return BedrockModel(self.bedrock_client, self.bedrock_client.model_id)

        # 2. MEDIUM → optionally Bedrock or Ollama fallback
        if complexity == "medium" and self.bedrock_client:
            return BedrockModel(self.bedrock_client, self.bedrock_client.model_id)

        # ------------------------------
        # 3. LOW → Ollama
        # ------------------------------
        # ------------------------------
        # Default -> Ollama fallback
        # ------------------------------
        if self.ollama_client:
            return OllamaModel(self.ollama_client)
            return OllamaModel(self.ollama_client)

        raise RuntimeError("No LLM provider available")

    def _estimate_complexity(self, query: str, context: str) -> str:
        q = query.lower()
        long_query = len(q.split()) > 12
        has_reasoning_words = any(
            w in q for w in ["explain", "compare", "why", "how", "architecture", "design"]
        )
        has_multiple_intents = " and " in q or " vs " in q

        if long_query or has_multiple_intents or has_reasoning_words:
            return "high"
        if len(q.split()) > 6:
            return "medium"
        return "low"
