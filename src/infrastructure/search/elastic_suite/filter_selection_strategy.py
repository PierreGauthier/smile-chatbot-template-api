from typing import List
from abc import ABC, abstractmethod

from domain.models import AttributeFilterValue

class FilterSelectionStrategy(ABC):
    def __init__(self, filters:List[AttributeFilterValue]):
        self.filters = filters

    @abstractmethod
    def reset(self):
        pass
    
    @abstractmethod
    def has_next(self) -> bool:
        pass

    @abstractmethod
    # Returns (selected filters, not-selected filters)
    def next(self) -> tuple[List[AttributeFilterValue], List[AttributeFilterValue]]:
        pass

