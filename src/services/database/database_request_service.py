from abc import ABC, abstractmethod

from models import ChatRequest

class DatabaseRequestService(ABC):

    @abstractmethod
    def get_request(self, user_id: str, session_id: str) -> ChatRequest:
        pass
    
    @abstractmethod
    def create_request(self, user_id: str) -> ChatRequest:
        pass

    @abstractmethod
    def update_request(self, new_request: ChatRequest)-> ChatRequest:
        pass