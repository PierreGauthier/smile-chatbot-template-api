from pydantic import BaseModel, Field

class LanguageField(BaseModel):
    code:str = Field(description="The code of the input message's detected language")