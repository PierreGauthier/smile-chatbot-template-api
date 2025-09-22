from dataclasses import dataclass
from typing import List

from domain.models import MessageData, SearchResponseItem

@dataclass
class SearchMessageData(MessageData):
    products:List[SearchResponseItem]
    
    def to_dict(self):
        my_dict = super().to_dict() 
        my_dict["products"] = [p.to_dict() for p in self.products]
        return my_dict
    
    @staticmethod
    def from_dict(data: dict):
        return SearchMessageData(
            content=data.get("content", ""),
            products=data.get("products", [])
        )