from index_filter import IndexFilter
from models import RequestDefinition, IndexFilterResult

class DefaultIndexFilter(IndexFilter):
    """Default"""

    def apply(self, request: RequestDefinition) -> bool:
        return True

    def get_index(self) -> IndexFilterResult:
        # Put it in the config file
        return IndexFilterResult(index_name="default_index")