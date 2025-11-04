from abc import ABC, abstractmethod

from domain.models import SearchContext

class SearchResponseBuilderStrategyAgent(ABC):
    
    @abstractmethod
    def apply(self, context:SearchContext):
        pass

    @abstractmethod
    def invoke(self, context:SearchContext):
        pass