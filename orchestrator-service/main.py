from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os

from orchestrator.pipeline import OrchestrationPipeline
from evaluation.runner import EvaluationRunner
from evaluation.dataset_loader import load_dataset

from agents.agent_executor import AgentExecutor
from agents.tool_registry import ToolRegistry
from agents.tools import (
    get_time,
    echo_tool,
    search_docs_tool,
)
from schemas.tool_models import GetTimeInput, GetTimeOutput,SearchDocsInput, SearchDocsOutput
from router.model_router import ModelRouter

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

def build_eval_agent():

    router = ModelRouter()

    model = router.select_model(
        query="evaluation",
        context=""
    )

    tool_registry = ToolRegistry()

    tool_registry.register(
        "get_time",
        get_time,
        input_model=GetTimeInput,
        output_model=GetTimeOutput
    )

    tool_registry.register(
        "search_docs",
        search_docs_tool,
        input_model=SearchDocsInput,
        output_model=SearchDocsOutput
    )

    tool_registry.register(
        "echo",
        echo_tool
    )
    
    return AgentExecutor(
        model=model,
        tool_registry=tool_registry
    )


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

@app.post("/evaluate")
def evaluate(payload: dict):

    agent = build_eval_agent()

    runner = EvaluationRunner(agent)

    dataset = payload["dataset"]

    result = runner.run_dataset(dataset)

    return result