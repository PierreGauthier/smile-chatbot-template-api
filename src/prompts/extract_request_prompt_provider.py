from typing import List
from typing import Annotated
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from prompts import PromptProvider
from models import ChatMessage

class ExtractRequestPromptProvider(PromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.prompt_name = settings.langsmith_extract_request_definition_prompt_name

    def get_prompt(self, history:List[ChatMessage]) -> ChatPromptTemplate:
        prompt = hub.pull(self.prompt_name)
        for message in history:
            msg = message.get_tuple_for_prompt()
            prompt.append(message=msg)
        return prompt
