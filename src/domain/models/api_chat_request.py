from pydantic import BaseModel, Field

class ApiChatRequest(BaseModel):
    """A chat API request"""
    user_id: str
    session_id: str | None = None
    message: str
    max_products: int | None = Field(default=10, ge=1, le=20, description="Maximum number of products to return (1-20)")