"""
==========================================================
NexusERP-AI — Conversation Memory
==========================================================

Manages conversation history per session.
Phase 1: in-memory only (no database persistence).
Phase 2: will store in ConversationMessage model.
==========================================================
"""


class ConversationMemory:
    """
    Stores message history for one conversation.

    Phase 1:
        In-memory only. History is lost when the
        request ends. Suitable for stateless APIs.

    Phase 2:
        Will persist to database using
        ConversationMessage model.
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self._messages: list = []

    def add(self, role: str, content: str) -> None:
        """
        Add a message to history.

        Parameters
        ----------
        role : str
            "user" or "assistant"
        content : str
        """
        self._messages.append({
            "role":    role,
            "content": content,
        })

        # Keep only the most recent messages
        if len(self._messages) > self.max_history:
            self._messages = self._messages[-self.max_history:]

    def get_messages(self) -> list:
        """Return all messages in history."""
        return list(self._messages)

    def clear(self) -> None:
        """Clear all history."""
        self._messages = []

    def __len__(self) -> int:
        return len(self._messages)