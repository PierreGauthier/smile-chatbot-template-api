from dataclasses import dataclass

from domain.models import AttributeFilterDefinition

@dataclass
class AttributeFilterDto(AttributeFilterDefinition):
    id:str
    options_type: str
    options:list
    
    def to_dict(self, attribute_id:int) -> dict:
        return {
            "id":self.id,
            "attribute_id":attribute_id,
            "label":self.label,
            "code":self.code,
            "type":self.type,
            "description":self.description,
            "options_type":self.options_type,
            "options":self.options
        }
    
    def from_dto(dto:dict):
        options = dto.get("options") or []
        return AttributeFilterDto(
            id=dto.get("id"),
            attribute_id=dto.get("attribute_id"),
            label=dto.get("label"),
            code=dto.get("code"),
            type=dto.get("type"),
            description=dto.get("description"),
            options_type=dto.get("options_type"),
            options=options,
        )