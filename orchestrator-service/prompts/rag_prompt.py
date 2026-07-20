RAG_PROMPT = """
[MODE: RAG]

User question:
{query}

Conversation:
{history}

Retrieved context:
{context}

Rules:
- Use retrieved context when it is relevant and helpful
- If the context is empty or incomplete, rely on general knowledge
- If context conflicts with general knowledge, prefer correctness over strict adherence
- Do not say "I don't know" unless the question is truly unanswerable
"""
