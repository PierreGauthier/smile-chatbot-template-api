from pydantic import BaseModel

class ApiChatRequest(BaseModel):
    """A chat API request"""
    user_id:str
    session_id: str | None = None
    message: str