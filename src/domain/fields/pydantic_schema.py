from dataclasses import dataclass

@dataclass
class PydanticSchema:
    name:str
    field_type:type
    required:bool
    description:str