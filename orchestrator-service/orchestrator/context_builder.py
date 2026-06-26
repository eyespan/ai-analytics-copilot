from prompts.system_prompt import SYSTEM_PROMPT
from prompts.rag_prompt import RAG_PROMPT
from prompts.code_prompt import CODE_PROMPT
from prompts.agent_prompt import AGENT_PROMPT
from prompts.summary_prompt import SUMMARY_PROMPT

from prompts.prompt_router import PromptRouter, PromptType


class PromptManager:

    def __init__(self):
        self.router = PromptRouter()

    def build_prompt(self, query, docs=None, history=None):

        prompt_type = self.router.classify(query)

        print(f"[PROMPT ROUTER] Query: {query}")
        print(f"[PROMPT ROUTER] Classified as: {prompt_type}")

        #history_text = self._format_history(history or [])
        history_text = ""

        if prompt_type == PromptType.CODE:
             prompt = SYSTEM_PROMPT + "\n\n" + CODE_PROMPT.format(
                query=query,
                history=history_text
             )
             return {
                "prompt": prompt,
                "type": prompt_type
             }

        if prompt_type == PromptType.AGENT:
            prompt = SYSTEM_PROMPT + "\n\n" + AGENT_PROMPT.format(
                query=query,
                history=history_text
            )
            return {
                "prompt": prompt,
                "type": prompt_type
             }

        if prompt_type == PromptType.SUMMARY:
            prompt = SYSTEM_PROMPT + "\n\n" + SUMMARY_PROMPT.format(
                query=query,
                history=history_text
            )
            return {
                "prompt": prompt,
                "type": prompt_type
             }

        # DEFAULT → RAG
        retrieved_text = self._format_docs(docs or [])

        prompt = SYSTEM_PROMPT + "\n\n" + RAG_PROMPT.format(
            query=query,
            context=retrieved_text,
            history=history_text
        )
        return {
                "prompt": prompt,
                "type": prompt_type
        }

    def _format_docs(self, docs):
        return "\n".join([
            f"{d.get('repo_name','')} "
            f"({d.get('language','Unknown')}) - "
            f"{d.get('description','')} "
            f"[rerank_score={round(d.get('rerank_score', 0), 2)}]"
            for d in docs[:5]
        ])

    def _format_history(self, history):
        return "\n".join([
            f"User: {h['query']}\nAssistant: {h['response']}"
            for h in history[-3:]
        ])