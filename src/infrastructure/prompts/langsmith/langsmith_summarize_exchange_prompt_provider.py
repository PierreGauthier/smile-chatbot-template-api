from typing import Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from domain.models import Language
from application.prompts import SummarizeExchangePromptProvider

from config import Settings, get_settings

class LangsmithSummarizeExchangePromptProvider(SummarizeExchangePromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_summary_exchange_prompt_name


    def get_prompt(self, lang:Language) -> ChatPromptTemplate:
        
        prompt: ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)
        # LANG not user for now
        # prompt = prompt.partial(language=lang.lang_name)
        return prompt