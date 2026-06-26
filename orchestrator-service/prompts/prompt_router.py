from dataclasses import dataclass


@dataclass
class PromptType:
        RAG = "rag"
        CODE = "code"
        AGENT = "agent"
        SUMMARY = "summary"
        DIRECT_LLM = "direct_llm"


class PromptRouter:

    def classify(self, query: str) -> str:
        q = query.lower()

        # -------------------------
        # CODE INTENT
        # -------------------------
        if any(k in q for k in [
            "write code", "python", "function", "class", "bug", "fix", "script"
        ]):
            return PromptType.CODE

        # -------------------------
        # AGENT / ARCHITECTURE INTENT
        # -------------------------
        if any(k in q for k in [ 
            "and then", "then", "workflow", "call tool",
            "search docs", "fetch", "multi-step"   
        ]):
            return PromptType.AGENT

        # -------------------------
        # SUMMARY INTENT
        # -------------------------
        if any(k in q for k in [
            "summarize", "tldr", "brief"
        ]):
            return PromptType.SUMMARY

        # -------------------------
        # HIGH reasoning intent → DIRECT LLM
        # -------------------------
        if any(k in q for k in [
            "explain", "compare", "why", "how", "architecture",
            "tradeoffs", "design", "cap theorem", "scalability"
        ]):
            return PromptType.DIRECT_LLM
        
        print(f"[PROMPT ROUTER] Query: {query}")

        # -------------------------
        # DEFAULT → RAG
        # -------------------------
        return PromptType.RAG