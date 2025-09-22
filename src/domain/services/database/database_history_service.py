from typing import List, TypeVar, Generic, Type
from abc import ABC, abstractmethod

from domain.models import ChatMessage

T = TypeVar('T', bound=ChatMessage)

class DatabaseHistoryService(ABC, Generic[T]):
    def __init__(self, message_class: Type[T]):
        self.message_class = message_class

    @abstractmethod
    def create_message_thread(self, user_id: str, message: str) -> T:
        pass
    
    @abstractmethod
    def get_message_thread(self, user_id: str, session_id: str) -> List[T]: 
        pass
    
    @abstractmethod
    def upsert_message(self, message:T):
        pass