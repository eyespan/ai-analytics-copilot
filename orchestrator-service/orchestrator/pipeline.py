from typing import Dict, Any, List, Generator
import json
import time

from router.model_router import ModelRouter, BaseModel
from memory.short_term import ConversationMemory
from streaming.sse import StreamEmitter
from rag_client import RagClient
#from prompts.system_prompt import SYSTEM_PROMPT
#from prompts.rag_prompt import RAG_PROMPT
from orchestrator.context_builder import PromptManager
from prompts.prompt_router import PromptType
from agents.agent_executor import AgentExecutor
from agents.tool_registry import ToolRegistry
from agents.tools import get_time, echo_tool, search_docs_tool


class OrchestrationPipeline:

    def __init__(self):
        self.rag = RagClient()
        self.prompt_manager = PromptManager()
        self.router = ModelRouter()
        self.memory = ConversationMemory()
        self.sse = StreamEmitter()  # renamed: was self.stream, which shadowed the stream() method
        self.tool_registry = ToolRegistry()
        self.tool_registry.register("get_time", get_time)
        self.tool_registry.register("echo", echo_tool)
        self.tool_registry.register("search_docs", search_docs_tool)

    def run(self, query: str, session_id: str, stream: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        history = self.memory.get(session_id)
        retrieval = self._retrieve(query)

        hybrid = retrieval.get("hybrid_results") or retrieval.get("results") or []
        reranked = self.rag.rerank(query, hybrid)
        result = self.prompt_manager.build_prompt(
            query=query,
            docs=reranked,
            history=history
        )
        context = result["prompt"]
        prompt_type = result["type"]
        print(f"[PIPELINE] Prompt type received: {prompt_type}")
        # model = self.router.select_model(query=query, context=context)
        model = self.router.select_model(
            query=query,
            context=context
        )

        # =========================================================
        # 5. 🔥 NEW: AGENT BRANCHING (THIS IS THE ONLY ADDITION)
        # =========================================================
        if prompt_type == PromptType.AGENT:
            executor = AgentExecutor(
                model=model,
                tool_registry=self.tool_registry
            )

            answer = executor.run(
                query=query,
                context=context
            )

            self.memory.append(session_id, query, answer)

            if stream:
                return self._stream_response(model, query, context, session_id)

            return {
                "answer": answer,
                "session_id": session_id,
                "model_used": model.name,
                "mode": "agent",
                "latency_ms": int((time.time() - start_time) * 1000),
            }

        if stream:
            # return generator directly — StreamingResponse consumes it
            return self._stream_response(model, query, context, session_id)

        answer = model.generate(prompt=context)
        if not answer or answer.strip() == "":
            answer = "I couldn't generate a response from the model."

        self.memory.append(session_id, query, answer)

        return {
            "answer": answer,
            "session_id": session_id,
            "model_used": model.name,
            "latency_ms": int((time.time() - start_time) * 1000),
            "retrieval": {
                "bm25": len(retrieval["bm25_results"]),
                "vector": len(retrieval["vector_results"]),
                "hybrid": len(retrieval["hybrid_results"])
            },
            "reranked_top": reranked[:3]
        }

    def _retrieve(self, query: str) -> Dict[str, Any]:
        return self.rag.debug_retrieval(query)

    #def _build_context(self, query: str, docs: List[Dict], history: List[Dict]) -> str:
    #    retrieved_text = "\n".join([
    #        f"{d.get('repo_name', '')}: {d.get('description', '')}"
    #        for d in docs[:5]
    #    ])
    #    history_text = "\n".join([
    #        f"User: {h['query']}\nAssistant: {h['response']}"
    #        for h in history[-3:]
    #    ])
    #    prompt = RAG_PROMPT.format(
    #        history=history_text,
    #        context=retrieved_text,
    #        query=query
    #    )
    #    return f"{SYSTEM_PROMPT}\n\n{prompt}"

    def _stream_response(
        self, model: BaseModel, query: str, context: str, session_id: str
    ) -> Generator[str, None, None]:
        """
        Yields SSE-formatted strings.
        model.stream() is contractually guaranteed to yield plain strings (see BaseModel).
        SSE formatting lives here and nowhere else.
        """
        full_response = ""

        for token in model.stream(prompt=context):
            full_response += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        yield f"data: {json.dumps({'token': '[DONE]'})}\n\n"

        self.memory.append(session_id, query, full_response)