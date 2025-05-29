from pydantic import BaseModel, Field

class RequestDefinitionField(BaseModel):
    """See **RequestDefinition class"""
    subject: int = Field(description="Conversation subject")
    ai_response: str = Field(description="The LLM question to complete the request")
