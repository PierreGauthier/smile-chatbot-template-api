from dataclasses import dataclass
from typing import List

from domain.models import MessageData, Source

@dataclass
class RagMessageData(MessageData):
    sources:List[Source]
    
    def to_dict(self):
        my_dict = super().to_dict() 
        my_dict["sources"] = [s.to_dict() for s in self.sources]
    
    @staticmethod
    def from_dict(data: dict):
        return RagMessageData(
            content=data.get("content", ""),
            sources=data.get("sources", [])
        )