import uuid
from typing import List
from dataclasses import dataclass

from models import FilterOptionDto

@dataclass
class AttributeFilterDto:
    id:str
    label:str
    code:str
    type:str
    description:str
    options:List[FilterOptionDto]

    def build_from_api_response(response:dict):
        label = response.get("attribute_label", None)
        code = response.get("attribute_code", None)
        type = response.get("attribute_type", None)
        description = response.get("filter_description", None)
        
        options_dicts = response.get("attribute_options", None)
        options:List[FilterOptionDto] = []
        if options_dicts:
            for option_dict in options_dicts:
                options.append(FilterOptionDto.build_from_api_response(option_dict))
        return AttributeFilterDto(
            id=str(uuid.uuid4()),
            label=label,
            code=code,
            type=type,
            description=description,
            options=options
        )
    
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
        options = [FilterOptionDto.from_dto() for o in options_dict]
        return AttributeFilterDto(
            id=dto.get("id"),
            attribute_id=dto.get("attribute_id"),
            label=dto.get("label"),
            code=dto.get("code"),
            type=dto.get("type"),
            description=dto.get("description"),
            options=options,
        )