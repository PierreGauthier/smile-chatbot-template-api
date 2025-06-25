from pydantic import BaseModel, Field

class IntentDefinitionField(BaseModel):
    is_intent: bool = Field(description="Whether the user's question is about Padel (paddle tennis) sport")
    chain_of_thoughts: str = Field(description="An explanation why you chose the value for `is_intent`")