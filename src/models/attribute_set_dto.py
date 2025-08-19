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

    @staticmethod
    def _extract_name(text: str) -> str:
        match = re.match(r'^[A-Za-z]{2,5}\s\[\d+\]\s(.+?)\s\(\d+\)$', text)
        if match:
            return match.group(1)
        return None

    @classmethod
    def build_from_api_response(cls, response:dict):
        attribute_set_id = response.get("attribute_set_id", 0)
        original_name = response.get("attribute_set_name", "-unknown-")
        name = cls._extract_name(original_name)
        description = response.get("attribute_set_description", "-")

        filters_dicts = response.get("filters", None)
        filters:List[AttributeFilterDto] = []
        if filters_dicts:
            for filters_dict in filters_dicts:
                filters.append(AttributeFilterDto.build_from_api_response(filters_dict, attribute_set_id))

        object =  AttributeSetDto(
            id=str(uuid.uuid4()),
            attribute_set_id=attribute_set_id,
            name = name.lower() if name else original_name,
            description=description,
            filters=filters
        )
        return object

    def to_dict(self, partition_key:str, partition_value:str) -> dict:
        return {
            partition_key:partition_value,
            "id":self.id,
            "attribute_set_id":self.attribute_set_id,
            "name":self.name,
            "description":self.description
        }