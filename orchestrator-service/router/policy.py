from dataclasses import dataclass
from enum import Enum


class ModelProvider(str, Enum):
    BEDROCK = "bedrock"
    OLLAMA = "ollama"
    OPENAI = "openai"


class QueryComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RoutingDecision:
    provider: ModelProvider
    complexity: QueryComplexity
    reason: str

    def to_dict(self):
        return {
            "provider": self.provider.value,
            "complexity": self.complexity.value,
            "reason": self.reason,
        }


class RoutingPolicy:

    """
    Central routing policy.

    The router supplies request metadata.
    This policy decides WHICH provider should answer.

    Provider selection can be explicitly requested through
    `preferred_provider`, while the existing complexity-based
    routing remains the default behaviour.

    This preserves the Level 6 routing behaviour while allowing
    Level 7 Settings to select the preferred LLM provider.
    """

    def choose(
        self,
        *,
        complexity: QueryComplexity,
        bedrock_available: bool,
        ollama_available: bool,
        prefer_local: bool = False,
        preferred_provider: ModelProvider | None = None,
    ) -> RoutingDecision:

        # --------------------------------------------------
        # Explicit provider preference
        #
        # Level 7 Settings can request a specific provider.
        # If that provider is unavailable, continue through
        # the existing routing policy rather than failing here.
        # --------------------------------------------------

        if preferred_provider == ModelProvider.BEDROCK:

            if bedrock_available:

                return RoutingDecision(
                    provider=ModelProvider.BEDROCK,
                    complexity=complexity,
                    reason="settings_provider",
                )

        if preferred_provider == ModelProvider.OLLAMA:

            if ollama_available:

                return RoutingDecision(
                    provider=ModelProvider.OLLAMA,
                    complexity=complexity,
                    reason="settings_provider",
                )

        # --------------------------------------------------
        # Explicit local preference
        # --------------------------------------------------

        if prefer_local and ollama_available:

            return RoutingDecision(
                provider=ModelProvider.OLLAMA,
                complexity=complexity,
                reason="local_preference",
            )

        # --------------------------------------------------
        # HIGH complexity
        # --------------------------------------------------

        if complexity == QueryComplexity.HIGH:

            if bedrock_available:

                return RoutingDecision(
                    provider=ModelProvider.BEDROCK,
                    complexity=complexity,
                    reason="high_complexity",
                )

            if ollama_available:

                return RoutingDecision(
                    provider=ModelProvider.OLLAMA,
                    complexity=complexity,
                    reason="bedrock_unavailable",
                )

        # --------------------------------------------------
        # MEDIUM complexity
        # --------------------------------------------------

        if complexity == QueryComplexity.MEDIUM:

            if ollama_available:

                return RoutingDecision(
                    provider=ModelProvider.OLLAMA,
                    complexity=complexity,
                    reason="bedrock_unavailable",
                )

        # --------------------------------------------------
        # LOW complexity
        # --------------------------------------------------

        if ollama_available:

            return RoutingDecision(
                provider=ModelProvider.OLLAMA,
                complexity=complexity,
                reason="simple_query",
            )

        if bedrock_available:

            return RoutingDecision(
                provider=ModelProvider.BEDROCK,
                complexity=complexity,
                reason="ollama_unavailable",
            )

        raise RuntimeError("No LLM providers available")