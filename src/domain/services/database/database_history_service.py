from typing import List
from abc import ABC, abstractmethod

from domain.models import ChatMessage

class DatabaseHistoryService(ABC):

    @abstractmethod
    def create_message_thread(self, user_id: str, message: str) -> ChatMessage:
        pass
    
    @abstractmethod
    def get_message_thread(self, user_id: str, session_id: str) -> List[ChatMessage]: 
        pass
    
    @abstractmethod
    def upsert_message(self, message:ChatMessage):
        pass