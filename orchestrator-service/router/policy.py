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
        """

        def choose(
            self,
            *,
            complexity: QueryComplexity,
            bedrock_available: bool,
            ollama_available: bool,
            prefer_local: bool = False,
        ) -> RoutingDecision:

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

                #if bedrock_available:

                #    return RoutingDecision(
                #       provider=ModelProvider.BEDROCK,
                #        complexity=complexity,
                #        reason="medium_complexity",
                #    )

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