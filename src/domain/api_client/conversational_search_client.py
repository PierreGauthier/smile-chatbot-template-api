from typing import List
from abc import abstractmethod

from domain.api_client import BaseClient
from domain.models import (
    FilteredSearchApiResponse, 
    AttributeFilterValue, 
    ProductFilterDetectionResult, 
    AttributeFilterDto,
    BaseContext
)

class ConversationalSearchClient(BaseClient):
    """Abstract client for conversational search APIs that expose filtered product search.

    Implementations must call the platform's search endpoint and return a ``FilteredSearchApiResponse``
    that reflects the provided filter detection results, selected filter DTOs, and requested page size.
    """
    def __init__(self, base_url: str):
        super().__init__(base_url)

    @abstractmethod
    def search(
            self, 
            filter_detection_result:ProductFilterDetectionResult,
            filters_dto:List[AttributeFilterDto],
            #attribute_set:str, 
            #term:str,
            #filters:List[AttributeFilterValue], 
            context:BaseContext,
            page_size:int
        ) -> FilteredSearchApiResponse:
        pass
