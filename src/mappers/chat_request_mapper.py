from models import ChatRequest
from mappers import RequestDefinitionMapper

class ChatRequestMapper:

    @staticmethod
    def to_dict(thread: ChatRequest) -> dict:
        return {
            "id": thread.session_id,
            "user_id": thread.user_id,
            "request": RequestDefinitionMapper.to_dict(thread.request)
        }
    
    @staticmethod
    def from_dict(data: dict) -> ChatRequest:
        return ChatRequest(
            user_id=data["user_id"],
            session_id=data["id"],
            request=RequestDefinitionMapper.from_dict(data["request"])
        )
