from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os

from orchestrator.pipeline import OrchestrationPipeline

pipeline = OrchestrationPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ollama client is already initialised in ModelRouter.__init__()
    # via env vars — nothing extra needed here unless injecting
    # Bedrock or OpenAI clients at startup:
    #
    # import boto3
    # pipeline.router.bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
    yield


app = FastAPI(title="Orchestrator Service", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: dict):
    result = pipeline.run(
        query=payload["query"],
        session_id=payload.get("session_id", "default"),
        stream=False
    )
    print("PIPELINE OUTPUT:", result)
    return result


@app.post("/ask-stream")
def ask_stream(payload: dict):
    return StreamingResponse(
        pipeline.run(
            query=payload["query"],
            session_id=payload.get("session_id", "default"),
            stream=True
        ),
        media_type="text/event-stream"
    )