from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import requests


app = FastAPI(title="API Gateway")


ORCHESTRATOR_URL = os.getenv(
    "ORCHESTRATOR_URL",
    "http://orchestrator-service",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "API Gateway Running"}


@app.post("/ask-stream")
def ask_stream(payload: dict):

    response = requests.post(
        f"{ORCHESTRATOR_URL}/ask-stream",
        json=payload,
        stream=True,
    )

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail="Orchestrator streaming request failed",
        )

    return StreamingResponse(
        response.iter_content(
            chunk_size=None
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )