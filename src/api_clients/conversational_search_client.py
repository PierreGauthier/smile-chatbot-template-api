from typing import List
from abc import abstractmethod

from api_clients import BaseClient
from models import SearchApiResponse, AttributeFilterValue

class ConversationalSearchClient(BaseClient):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    @abstractmethod
    def search_products(
            self, 
            attribute_set:str, 
            filters:List[AttributeFilterValue], 
            page_size:int
        ) -> SearchApiResponse:
        pass