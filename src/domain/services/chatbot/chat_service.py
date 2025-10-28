from abc import ABC, abstractmethod

from domain.models import ChatServiceResult

class ChatService(ABC):
    """Defines the interface chatbot adapters must implement."""

    @abstractmethod
    def invoke(self, message: str, user_id: str, session_id: str = None) -> ChatServiceResult:
        """Trigger a chatbot response for the provided user session."""
        pass
