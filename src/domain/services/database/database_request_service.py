from typing import List
from abc import ABC, abstractmethod

from domain.models import UserRequestDto

class DatabaseRequestService(ABC):

    @abstractmethod
    def create_request(self, user_id:str, session_id:str, attribute_id:int, data:dict) -> UserRequestDto:
        pass

    @abstractmethod
    def get_requests(self, user_id:str, session_id:str) -> List[UserRequestDto]:
        pass

    @abstractmethod
    def update_request(self, request:UserRequestDto):
        pass