from typing import Generator, Optional
import os
from clients.ollama_client import OllamaClient


class BaseModel:
    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Must yield plain strings — no SDK objects, no raw bytes."""
        raise NotImplementedError


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

    def stream(self, prompt: str) -> Generator[str, None, None]:
        # Bedrock returns an EventStream — extract text chunks here,
        # never expose SDK objects to the pipeline layer
        event_stream = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body={"prompt": prompt}
        )
        for event in event_stream.get("body", []):
            chunk = event.get("chunk", {})
            if text := chunk.get("bytes", b"").decode("utf-8", errors="ignore"):
                yield text


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

    def stream(self, prompt: str) -> Generator[str, None, None]:
        # OpenAI SDK stream returns delta objects — unwrap to strings here
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
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
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        )

    def select_model(self, query: str, context: str = "") -> BaseModel:
        complexity = self._estimate_complexity(query, context)

        if complexity == "high" and self.bedrock_client:
            return BedrockModel(self.bedrock_client, "anthropic.claude-3-sonnet-20240229-v1:0")

        if complexity == "medium":
            if self.openai_client:
                return OpenAIModel(self.openai_client)
            if self.bedrock_client:
                return BedrockModel(self.bedrock_client, "anthropic.claude-3-haiku-20240307-v1:0")

        if self.ollama_client:
            return OllamaModel(self.ollama_client)

        if self.bedrock_client:
            return BedrockModel(self.bedrock_client, "anthropic.claude-3-haiku-20240307-v1:0")

        raise RuntimeError("No LLM provider available")

    def _estimate_complexity(self, query: str, context: str) -> str:
        q = query.lower()
        long_query = len(q.split()) > 12
        has_reasoning_words = any(w in q for w in [
            "explain", "compare", "why", "how", "architecture", "design"
        ])
        has_multiple_intents = " and " in q or " vs " in q

        if long_query or has_multiple_intents or has_reasoning_words:
            return "high"
        if len(q.split()) > 6:
            return "medium"
        return "low"