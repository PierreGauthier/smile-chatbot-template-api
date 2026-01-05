from pydantic import BaseModel, Field

class ChitChatField(BaseModel):
    is_chit_chat:bool = Field(description="Whether the last message of the user is a **chit-chat message** that does not contribute new search parameters")
    category:str|None = Field(description="Category name or 'None'")
    response:str|None = Field(description="LLM response to the user if chit-chat, or 'None' if actionable")
    missing_info:str|None = Field(description="What information is still needed, if applicable")