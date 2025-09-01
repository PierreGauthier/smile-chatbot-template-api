from typing import Annotated
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from prompts import PromptProvider

class EmptySearchResponseBuilderPromptProvider(PromptProvider):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.prompt_name = settings.langsmith_empty_search_response_builder_prompt_name

    def get_prompt(self) -> ChatPromptTemplate:
        prompt = hub.pull(self.prompt_name)
        return prompt