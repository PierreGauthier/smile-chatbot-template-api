from models import ChatThread
from mappers import ChatMessageMapper

class ChatThreadMapper:
    @staticmethod
    def to_dict(thread: ChatThread) -> dict:
        return {
            "id": thread.session_id,
            "user_id": thread.user_id,
            "messages": [
                ChatMessageMapper.to_dict(m) 
                for m in thread.messages
            ]
        }
    
    @staticmethod
    def from_dict(data: dict) -> ChatThread:
        messages = [
            ChatMessageMapper.from_dict(m) 
            for m in data.get("messages", [])
        ]
        return ChatThread(
            user_id=data["user_id"],
            session_id=data["id"],
            messages=messages
        )
