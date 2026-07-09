import random

from sentence_transformers import CrossEncoder

# Lightweight reranker model (good balance for M2 Max)
_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def _format_doc(doc: dict) -> str:
    """
    Convert OpenSearch document into reranker-friendly text
    """
    return f"""
Repo: {doc.get('repo_name', '')}
Description: {doc.get('description', '')}
Language: {doc.get('language', '')}
""".strip()


def rerank(query: str, docs: list, top_k: int = None):
    """
    Cross-encoder reranking of retrieved documents
    """

    if not docs:
        return []

    #### Level 4 Addition: Random shuffle before reranking to mitigate any bias from retrieval order
    docs_copy = docs.copy()
    random.shuffle(docs_copy)

    # Build query-document pairs
    pairs = [(query, _format_doc(doc)) for doc in docs_copy]

    # Predict relevance scores
    scores = _model.predict(pairs)

    # Attach scores
    for doc, score in zip(docs_copy, scores):
        doc["rerank_score"] = float(score)

    # Sort by reranker score
    reranked = sorted(docs_copy, key=lambda x: x["rerank_score"], reverse=True)

    # Optional truncation
    if top_k:
        reranked = reranked[:top_k]

    return reranked
