from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# Request schema
# -------------------------


class EmbeddingRequest(BaseModel):
    text: str


# -------------------------
# Health
# -------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# Root
# -------------------------


@app.get("/")
def root():
    return {"message": "Embedding Service Running"}


# -------------------------
# Embedding endpoint
# -------------------------


@app.post("/embed")
def embed(request: EmbeddingRequest):

    vector = model.encode(request.text).tolist()

    return {"embedding": vector}
