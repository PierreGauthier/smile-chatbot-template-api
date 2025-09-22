from domain.models import MessageData
from dataclasses import dataclass

@dataclass
class ChatMessage:
    session_id:str
    user_id:str
    type:str
    data:MessageData
    id:str = None

    # @classmethod
    # def build_human_message(cls, session_id:str, user_id:str, content:str, id:str=None):
    #     return ChatMessage(id=id, session_id=session_id, user_id=user_id, type="human", data=MessageData(content=content))
    
    # @classmethod
    # def build_ai_message(cls, session_id:str, user_id:str, content:str, id:str=None):
    #     return ChatMessage(id=id, session_id=session_id, user_id=user_id, type="ai", data=MessageData(content=content))
    
    def to_dict(self) -> dict:
        data = self.data.to_dict() if self.data else {}
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "type": self.type,
            "data": data
        }
    
    @staticmethod
    def from_dict(data: dict):
        return ChatMessage(
            id=data.get("id", ""),
            session_id=data.get("session_id", ""),
            user_id=data.get("user_id", ""),
            type=data.get("type", ""),
            data=MessageData.from_dict(data.get("data", {})),
        )