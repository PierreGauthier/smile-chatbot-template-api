from typing import List, TypeVar, Generic, Type
from abc import ABC, abstractmethod

from domain.models import ChatMessage
T = TypeVar('T', bound=ChatMessage)

class DatabaseHistoryService(ABC, Generic[T]):
    """Describes the operations a database-backed chat history store must expose."""

    def __init__(self, message_class: Type[T]):
        self.message_class = message_class

    @abstractmethod
    def create_message_thread(self, user_id: str, message: str) -> T:
        """Create a new thread seeded with the initial user message."""
        pass
    
    @abstractmethod
    def get_message_thread(self, user_id: str, session_id: str) -> List[T]: 
        """Return the ordered messages for a particular user and session."""
        pass
    
    @abstractmethod
    def upsert_message(self, message:T):
        """Insert or update a chat message in the backing store."""
        pass
