from fastapi import FastAPI
from orchestrator.pipeline import OrchestrationPipeline
from router.model_router import ModelRouter
from clients.ollama_client import OllamaClient
#from streaming.sse import sse_response
from streaming.sse import StreamEmitter
from fastapi.responses import StreamingResponse
import os


app = FastAPI(title="Orchestrator Service")


pipeline = OrchestrationPipeline()


@app.on_event("startup")
def setup_router():
    router = pipeline.router

    # 👇 THIS IS THE MISSING PIECE
    router.ollama_client = OllamaClient(
        base_url="http://ollama:11434",
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: dict):

    query = payload["query"]
    session_id = payload.get("session_id", "default")

    result = pipeline.run(
        query=query,
        session_id=session_id,
        stream=False
    )

    return result



@app.post("/ask-stream")
def ask_stream(payload: dict):

    stream_gen = pipeline.run(
        query=payload["query"],
        session_id=payload.get("session_id", "default"),
        stream=True   # 🔥 THIS IS REQUIRED
    )

    return StreamingResponse(
        stream_gen,
        media_type="text/event-stream"
    )