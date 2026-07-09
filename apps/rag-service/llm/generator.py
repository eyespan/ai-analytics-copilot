from clients.ollama_client import generate
from config import MAX_CONTEXT_DOCS
from llm.prompts import RAG_PROMPT


def build_context(results):
    return "\n---\n".join(
        [
            f"Repository: {r['repo_name']}\n"
            f"Description: {r['description']}\n"
            f"Language: {r['language']}"
            for r in results
        ]
    )


def generate_answer(query: str, results: list):

    context_results = results[:MAX_CONTEXT_DOCS]

    context = build_context(context_results)

    prompt = RAG_PROMPT.format(context=context, question=query)

    return generate(prompt)
