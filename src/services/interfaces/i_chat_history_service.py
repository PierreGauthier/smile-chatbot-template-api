from abc import ABC, abstractmethod
from langchain_core.chat_history import BaseChatMessageHistory

class IChatHistoryService(ABC):
    @abstractmethod
    def get_history(self, session_id: str, user_id: str) -> BaseChatMessageHistory:
        pass