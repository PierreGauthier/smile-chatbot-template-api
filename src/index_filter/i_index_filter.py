from abc import ABC, abstractmethod

from models import RequestDefinition, IndexFilterResult

class IIndexFilter(ABC):
    @abstractmethod
    def apply(self, request: RequestDefinition) -> bool:
        pass

    @abstractmethod
    def get_index(self) -> IndexFilterResult:
        pass