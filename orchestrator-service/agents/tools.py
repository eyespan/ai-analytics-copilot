from datetime import datetime


def get_time(_: dict) -> str:
    # return datetime.utcnow().isoformat()
    return {"current_time": datetime.utcnow().isoformat()}


def echo_tool(args: dict) -> str:
    return f"Echo: {args.get('text', '')}"


def search_docs_tool(args: dict) -> str:
    from rag_client import RagClient

    query = args.get("query", "").strip()
    rag = RagClient()

    results = rag.debug_retrieval(query)

    if "error" in results:
        return "[DOC_ERROR] retrieval system unavailable"

    docs = results.get("hybrid_results", [])[:3]

    if not docs:
        return "[DOC_EMPTY] no documents found"

    return "[DOC_RESULTS]\n" + "\n".join(
        [f"{d.get('repo_name')} - {d.get('description')}" for d in docs]
    )
