import uuid
import re
from typing import List
from dataclasses import dataclass

from models import AttributeFilterDto

@dataclass
class AttributeSetDto:
    id:str
    attribute_set_id:int
    name:str
    description:str
    filters: List[AttributeFilterDto]

    def to_dict(self, partition_key:str, partition_value:str) -> dict:
        return {
            partition_key:partition_value,
            "id":self.id,
            "attribute_set_id":self.attribute_set_id,
            "name":self.name,
            "description":self.description
        }