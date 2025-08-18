from abc import ABC, abstractmethod

from models import ChatServiceResult

class ChatService(ABC):
    @abstractmethod
    def invoke(self, message: str, user_id: str, session_id: str = None) -> ChatServiceResult:
        pass