from abc import ABC, abstractmethod

from domain.models import SearchServiceResult

class SearchService(ABC):
    @abstractmethod
    def invoke(self, message: str, user_id: str, session_id: str = None) -> SearchServiceResult:
        pass