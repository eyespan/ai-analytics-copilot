from memory.conversation_store import ConversationStore


class ConversationMemory:
    """
    Wrapper over ClickHouse-based ConversationStore
    (used by orchestrator pipeline for Level 5 memory)
    """

    def __init__(self):
        self.store = ConversationStore()

    def get(self, session_id: str, limit: int = 5):
        return self.store.get(session_id, limit)

    def append(self, session_id: str, query: str, response: str, metadata=None):
        return self.store.append(session_id, query, response, metadata)

    def clear(self, session_id: str):
        return self.store.clear(session_id)