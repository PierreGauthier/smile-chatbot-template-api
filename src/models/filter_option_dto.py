from dataclasses import dataclass

@dataclass
class FilterOptionDto:
    key:str
    value:str

    def build_from_api_response(response:dict):
        return FilterOptionDto(
            key=response.get("key", None),
            value=response.get("value", None)
        )
    
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