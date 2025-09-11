from typing import List
from abc import ABC, abstractmethod

from domain.models import AttributeSetDto, AttributeFilterDto

class DatabaseAttributesSetupService(ABC):

    @abstractmethod
    def insert_attribute_set(self, attribute_set:AttributeSetDto):
        pass

    @abstractmethod
    def get_attribute_set(self, attribute_set_id:int) -> AttributeSetDto:
        pass
    
    @abstractmethod
    def get_attribute_set_by_name(self, attribute_set_name:str) -> AttributeSetDto:
        pass

    @abstractmethod
    def list_attribute_sets(self) -> List[AttributeSetDto]:
        pass

    @abstractmethod
    def insert_filters(self, attribute_set_id:int, filters:List[AttributeFilterDto]): 
        pass
    
    @abstractmethod
    def get_filters(self, attribute_set_id:int) -> List[AttributeFilterDto]:
        pass