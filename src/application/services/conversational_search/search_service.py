from abc import ABC, abstractmethod

from domain.models import SearchServiceResult

class SearchService(ABC):
    """Defines the contract any conversational search backend must implement."""

    @abstractmethod
    def invoke(self, message: str, user_id: str, session_id: str = None) -> SearchServiceResult:
        """
        Execute a conversational search request.

        :param message: The latest utterance from the user or assistant.
        :param user_id: Stable identifier for the end user issuing the request.
        :param session_id: Optional conversational session identifier.
        :returns: A structured result describing answer candidates and metadata.
        """
        pass
