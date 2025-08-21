from typing import Any
from dataclasses import dataclass

@dataclass
class UserRequestDto:
    id:str
    user_id:str
    session_id:str
    attribute_id:int
    data:dict

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "attribute_id": self.attribute_id,
            "data": self.data or {}
        }
    
    def from_dict(document:dict):
        return UserRequestDto(
            id=document["id"],
            user_id=document["user_id"],
            session_id=document["session_id"],
            attribute_id=int(document["attribute_id"]),
            data=document.get("data", {}) or {}
        )