from typing import List
from dataclasses import dataclass

from domain.models import AttributeFilterDto, AttributeSetDefinition

@dataclass
class AttributeSetDto(AttributeSetDefinition):
    id:str
    code:str
    description:str
    filters: List[AttributeFilterDto]

    def to_dict(self, partition_key:str, partition_value:str) -> dict:
        return {
            partition_key:partition_value,
            "id":self.id,
            "attribute_set_id":self.attribute_set_id,
            "code": self.code,
            "name":self.name,
            "description":self.description
        }