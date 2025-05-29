from abc import ABC, abstractmethod

from models import RagChatServiceResult

class IChatService(ABC):
    @abstractmethod
    def invoke(self, message: str, user_id: str, session_id: str = None) -> RagChatServiceResult:
        pass