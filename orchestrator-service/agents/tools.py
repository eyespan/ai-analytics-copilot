from datetime import datetime


def get_time(_: dict) -> str:
    return datetime.utcnow().isoformat()


def echo_tool(args: dict) -> str:
    return f"Echo: {args.get('text', '')}"


def search_docs_tool(args: dict) -> str:
    from rag_client import RagClient

    query = args.get("query", "").strip()

    # expand short queries
    if len(query.split()) <= 2:
        query = f"{query} deep learning framework documentation"
        rag = RagClient()

    results = rag.debug_retrieval(query)

    print("[RAG DEBUG]", results)

    docs = results.get("hybrid_results", [])[:3]

    if not docs:
        return "[DOC] No relevant documents found for query"

    return "\n".join([
        f"[DOC] repo={d.get('repo_name')} | desc={d.get('description')}"
        for d in docs
    ]) or "[DOC] no results found"