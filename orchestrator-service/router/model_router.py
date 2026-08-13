import os
from typing import Generator

from clients.bedrock_client import BedrockClient
from clients.ollama_client import OllamaClient

from router.policy import (
    ModelProvider,
    QueryComplexity,
    RoutingDecision,
    RoutingPolicy,
)


# ==========================================================
# Base Models
# ==========================================================


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

    def __init__(self, client, model="gpt-4o-mini"):

        super().__init__(f"openai:{model}")

        self.client = client
        self.model = model

    def generate(self, prompt: str) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content

    def stream(self, prompt: str) -> Generator[str, None, None]:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            stream=True,
        )

        for chunk in response:

            text = chunk.choices[0].delta.content or ""

            if text:
                yield text


class OllamaModel(BaseModel):

    def __init__(self, client, model="qwen2.5:3b"):

        super().__init__(f"ollama:{model}")

        self.client = client
        self.model = model

    def generate(self, prompt: str) -> str:

        response = self.client.generate(prompt)

        if isinstance(response, dict):
            return response.get("response", "")

        return response

    def stream(self, prompt: str):

        yield from self.client.stream_generate(prompt)


# ==========================================================
# Model Router
# ==========================================================


class ModelRouter:

    def __init__(self):

        self.policy = RoutingPolicy()

        self.last_decision: RoutingDecision | None = None

        # --------------------------------------------------
        # Provider configuration
        # --------------------------------------------------

        self.default_provider = os.getenv(
            "DEFAULT_PROVIDER",
            "ollama",
        ).lower()

        self.preferred_provider = self._parse_provider(
            self.default_provider
        )

        # --------------------------------------------------
        # Ollama
        # --------------------------------------------------

        self.ollama_client = OllamaClient(
            base_url=os.getenv(
                "OLLAMA_HOST",
                "http://ollama:11434",
            ),
            model=os.getenv(
                "OLLAMA_MODEL",
                "qwen2.5:3b",
            ),
        )

        # --------------------------------------------------
        # Bedrock
        # --------------------------------------------------

        self.bedrock_client = None

        if os.getenv(
            "BEDROCK_ENABLED",
            "true",
        ).lower() == "true":

            self.bedrock_client = BedrockClient(
                model_id=os.getenv(
                    "BEDROCK_MODEL_ID",
                    "anthropic.claude-3-haiku-20240307-v1:0",
                )
            )

    # ======================================================
    # Provider Parsing
    # ======================================================

    @staticmethod
    def _parse_provider(
        provider: str,
    ) -> ModelProvider | None:

        try:

            return ModelProvider(provider)

        except ValueError:

            print(
                "[ROUTER]",
                f"Unsupported DEFAULT_PROVIDER='{provider}'. "
                "Falling back to normal routing policy.",
            )

            return None

    # ======================================================
    # NEW PRODUCTION ROUTING ENTRY POINT
    # ======================================================

    def route(
        self,
        query: str,
        context: str = "",
    ) -> RoutingDecision:

        complexity = self._estimate_complexity(
            query,
            context,
        )

        decision = self.policy.choose(
            complexity=complexity,

            bedrock_available=(
                self.bedrock_client is not None
            ),

            ollama_available=(
                self.ollama_client is not None
            ),

            prefer_local=os.getenv(
                "PREFER_LOCAL_LLM",
                "false",
            ).lower() == "true",

            preferred_provider=self.preferred_provider,
        )

        self.last_decision = decision

        print(
            "[ROUTER]",
            f"provider={decision.provider.value}",
            f"complexity={decision.complexity.value}",
            f"reason={decision.reason}",
        )

        return decision

    # ======================================================
    # Decision -> Executable Model
    # ======================================================

    def get_model(
        self,
        decision: RoutingDecision,
    ) -> BaseModel:

        if decision.provider == ModelProvider.BEDROCK:

            if not self.bedrock_client:

                raise RuntimeError(
                    "Bedrock selected but unavailable"
                )

            return BedrockModel(
                self.bedrock_client,
                self.bedrock_client.model_id,
            )

        if decision.provider == ModelProvider.OLLAMA:

            return OllamaModel(
                self.ollama_client,
                self.ollama_client.model,
            )

        raise RuntimeError(
            f"Unsupported provider: {decision.provider}"
        )

    # ======================================================
    # Backward Compatibility
    # ======================================================

    def select_model(
        self,
        query: str,
        context: str = "",
    ) -> BaseModel:

        decision = self.route(
            query=query,
            context=context,
        )

        return self.get_model(decision)

    # ======================================================
    # Complexity Estimation
    # ======================================================

    def _estimate_complexity(
        self,
        query: str,
        context: str = "",
    ) -> QueryComplexity:

        q = query.lower()

        long_query = len(q.split()) > 12

        reasoning = any(
            word in q
            for word in (
                "why",
                "how",
                "compare",
                "architecture",
                "design",
                "explain",
            )
        )

        multiple_intents = (
            " and " in q
            or " vs " in q
        )

        if (
            long_query
            or reasoning
            or multiple_intents
        ):

            return QueryComplexity.HIGH

        if len(q.split()) > 6:

            return QueryComplexity.MEDIUM

        return QueryComplexity.LOW

    # ======================================================
    # Observability
    # ======================================================

    @property
    def routing_decision(
        self,
    ) -> RoutingDecision | None:

        return self.last_decision