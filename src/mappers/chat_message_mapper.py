from models import ChatMessage

class ChatMessageMapper:
    @staticmethod
    def to_dict(message: ChatMessage) -> dict:
        return {
            "type": message.type,
            "message": message.message
        }
    
    @staticmethod
    def from_dict(data: dict) -> ChatMessage:
        return ChatMessage(
            type=data.get("type", ""),
            message=data.get("message", "")
        )