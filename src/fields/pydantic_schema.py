from dataclasses import dataclass

@dataclass
class PydanticSchema:
    name:str
    type:str
    required:bool
    description:str