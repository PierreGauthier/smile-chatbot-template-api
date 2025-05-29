from models import RequestDefinitionField

class RequestDefinitionFieldMapper:
    @staticmethod
    def to_dict(request: RequestDefinitionField) -> dict:
        return {
            "subject": request.subject,
            "ai_response": request.ai_response
        }
    
    @staticmethod
    def from_dict(data: dict) -> RequestDefinitionField:
        return RequestDefinitionField(
            subject = data["device_id"],
            ai_response = data["ai_response"]
        )