import uuid
from typing import List
from dataclasses import dataclass

from domain.models import FilterOptionDto, AttributeFilterDefinition

@dataclass
class AttributeFilterDto(AttributeFilterDefinition):
    id:str
    options:List[FilterOptionDto]
    
    def to_dict(self, attribute_id:int) -> dict:
        options = [option.to_dict() for option in self.options]
        return {
            "id":self.id,
            "attribute_id":attribute_id,
            "label":self.label,
            "code":self.code,
            "type":self.type,
            "description":self.description,
            "options":options
        }
    
    def from_dto(dto:dict):
        options_dict = dto.get("options") or []
        options = [FilterOptionDto.from_dto(o) for o in options_dict]
        return AttributeFilterDto(
            id=dto.get("id"),
            attribute_id=dto.get("attribute_id"),
            label=dto.get("label"),
            code=dto.get("code"),
            type=dto.get("type"),
            description=dto.get("description"),
            options=options,
        )