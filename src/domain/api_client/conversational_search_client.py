from typing import List
from abc import abstractmethod

from domain.api_client import BaseClient
from domain.models import SearchApiResponse, AttributeFilterValue, ProductFilterDetectionResult, AttributeFilterDto

class ConversationalSearchClient(BaseClient):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    @abstractmethod
    def search_products(
            self, 
            filter_detection_result:ProductFilterDetectionResult,
            filters_dto:List[AttributeFilterDto],
            #attribute_set:str, 
            #term:str,
            #filters:List[AttributeFilterValue], 
            page_size:int
        ) -> SearchApiResponse:
        pass