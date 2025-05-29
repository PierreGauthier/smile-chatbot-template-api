from typing import List
from abc import ABC, abstractmethod

from models import ChatThread, ChatMessage

class IDatabaseHistoryService(ABC):

    @abstractmethod
    def get_chat_thread(self, user_id: str, session_id: str) -> ChatThread:
        pass
    
    @abstractmethod
    def get_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        pass
    
    @abstractmethod
    def insert_message(self, user_id: str, session_id: str, new_message:ChatMessage) -> ChatMessage:
        pass

    @abstractmethod
    def insert_human_message(self, user_id: str, session_id: str, message:str) -> ChatMessage:
        pass
    
    @abstractmethod
    def insert_ai_message(self, user_id: str, session_id: str, message:str) -> ChatMessage:
        pass
    
    @abstractmethod
    def create_chat_thread(self, user_id: str) -> ChatThread:
        pass
