from dataclasses import dataclass

@dataclass
class FilterOptionDto:
    key:str
    value:str
    
    def to_dict(self) -> dict:
        return {
            "key":self.key,
            "value":self.value
        }
    
    def from_dto(dto:dict):
        return FilterOptionDto(
            key=dto.get("key"),
            value=dto.get("value")
        )