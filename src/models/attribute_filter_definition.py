from dataclasses import dataclass

@dataclass
class AttributeFilterDefinition:
    attribute_id:int
    label:str
    code:str
    type:str
    description:str