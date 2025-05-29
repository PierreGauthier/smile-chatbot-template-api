from models import RequestDefinition

class RequestDefinitionMapper:
    @staticmethod
    def to_dict(request: RequestDefinition) -> dict:
        return {
            "subject": request.subject
        }
    
    @staticmethod
    def from_dict(data: dict) -> RequestDefinition:
        return RequestDefinition(
            subject = data["subject"]
        )