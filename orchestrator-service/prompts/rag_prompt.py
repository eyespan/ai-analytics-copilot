
RAG_PROMPT = """
[MODE: RAG]

User question:
{query}

Conversation:
{history}

Retrieved context:
{context}

Rules:
- Use ONLY retrieved context
- If missing info, say "I don't know"
"""