from typing import List

from domain.models import AttributeFilterValue
from infrastructure.search.elastic_suite import FilterSelectionStrategy

class OneFilterSelectionStrategy(FilterSelectionStrategy):
    def __init__(self, filters: List[AttributeFilterValue]):
        super().__init__(filters)
        self._current_index = 0
    
    def reset(self):
        self._current_index = 0

    def has_next(self) -> bool:
        return self._current_index < len(self.filters)

    def next(self) -> tuple[List[AttributeFilterValue], List[AttributeFilterValue]]:
        if not self.has_next():
            raise StopIteration

        selected_filter = self.filters[self._current_index]
        not_selected_filters = self.filters[:self._current_index] + self.filters[self._current_index + 1 :]
        self._current_index += 1
        return [selected_filter], not_selected_filters
