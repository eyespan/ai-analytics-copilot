from typing import Dict, Any, List, Optional
import time

from router.model_router import ModelRouter
from memory.short_term import ConversationMemory
from streaming.sse import StreamEmitter

from rag_client import RagClient   # wrapper over rag-service APIs

class OrchestrationPipeline:
    """
    Level 5 Brain:
    - controls retrieval
    - controls reranking
    - builds LLM context
    - selects model (Bedrock/OpenAI/Ollama)
    - handles memory
    - streams response
    """

    def __init__(self):
        self.rag = RagClient()
        self.router = ModelRouter()
        self.memory = ConversationMemory()
        self.stream = StreamEmitter()

    # =========================
    # MAIN ENTRYPOINT
    # =========================
    def run(self, query: str, session_id: str, stream: bool = False) -> Dict[str, Any]:

        start_time = time.time()

        # -------------------------
        # 1. Load conversation memory
        # -------------------------
        history = self.memory.get(session_id)

        # -------------------------
        # 2. Retrieval (Level 4 engine)
        # -------------------------
        retrieval = self._retrieve(query)

        # -------------------------
        # 3. Rerank (cross-encoder)
        # -------------------------
        hybrid = retrieval.get("hybrid_results") or retrieval.get("results") or []
        reranked = self.rag.rerank(query, hybrid)
    

        # -------------------------
        # 4. Context building (critical for grounding)
        # -------------------------
        context = self._build_context(query, reranked, history)

        # -------------------------
        # 5. Select model (Bedrock/OpenAI/Ollama)
        # -------------------------
        model = self.router.select_model(
            query=query,
            context=context
        )

        # -------------------------
        # 6. LLM call (stream or sync)
        # -------------------------
        #if stream:
        #    return self._stream_response(model, query, context, session_id)
        if stream:
            return self._stream_response(model, query, context, session_id)
        
        

        answer = model.generate(
            prompt=context
        )

        if not answer or answer.strip() == "":
            answer = "I couldn't generate a response from the model."

        # -------------------------
        # 7. Save memory
        # -------------------------
        self.memory.append(session_id, query, answer)

        # -------------------------
        # 8. Observability metadata
        # -------------------------
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

    # =========================
    # RETRIEVAL LAYER (Level 4)
    # =========================
    def _retrieve(self, query: str) -> Dict[str, Any]:
        return self.rag.debug_retrieval(query)

    # =========================
    # CONTEXT BUILDER (VERY IMPORTANT)
    # =========================
    def _build_context(self, query: str, docs: List[Dict], history: List[Dict]) -> str:

        retrieved_text = "\n".join([
            f"{d.get('repo_name','')}: {d.get('description','')}"
            for d in docs[:5]
        ])

        history_text = "\n".join([
            f"User: {h['query']}\nAssistant: {h['response']}"
            for h in history[-3:]
        ])

        return f"""
You are a precise technical assistant for code and ML systems.

IMPORTANT RULES:
- Use ONLY the retrieved knowledge below.
- If the answer is not in the context, say "I don't know based on the provided data".
- Do not return empty responses.
- Be concise and technical.

-----------------
Conversation Memory:
{history_text}

-----------------
Retrieved Knowledge:
{retrieved_text}

-----------------
User Question:
{query}

Answer clearly using the retrieved repositories and explain briefly.
"""

    # =========================
    # STREAMING MODE
    # =========================
    def _stream_response(self, model, query, context, session_id):

        response_stream = model.stream(prompt=context)

        full_response = ""

        for chunk in response_stream:   # OK because model.stream is sync generator
            token = chunk
            full_response += token
            yield self.stream.emit(token)

         # ✅ FINAL EVENT (critical fix)
        yield self.stream.emit("[DONE]")

        self.memory.append(session_id, query, full_response)

   

    def stream(self, query: str, session_id: str):

        history = self.memory.get(session_id)
        retrieval = self._retrieve(query)
        reranked = self.rag.rerank(query, retrieval["hybrid_results"])

        context = self._build_context(query, reranked, history)

        model = self.router.select_model(query=query, context=context)

        for chunk in model.stream(prompt=context):
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        yield "data: [DONE]\n\n"