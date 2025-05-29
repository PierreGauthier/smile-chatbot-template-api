from models import RagChatbotMessage
from mappers import RequestDefinitionFieldMapper

class RagChatbotMessageMapper:
    @staticmethod
    def to_dict(message: RagChatbotMessage) -> dict:
        return {
            "is_ai_message": message.is_ai_message,
            "message": RequestDefinitionFieldMapper.to_dict(message.message) if message.is_ai_message else message.message
        }
    
    @staticmethod
    def from_dict(data: dict) -> RagChatbotMessage:
        is_ai = data.get("is_ai_message", "")
        return RagChatbotMessage(
            is_ai_message = is_ai,
            message = RequestDefinitionFieldMapper.from_dict(data.get("message", None)) if is_ai else data.get("message", None)
        )