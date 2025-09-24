from typing import Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from domain.models import Language
from application.prompts import SummarizeExchangePromptProvider

from config import Settings, get_settings

class LangsmithSummarizeExchangePromptProvider(SummarizeExchangePromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.prompt_name = settings.langsmith_summary_exchange_prompt_name


    def get_prompt(self, lang:Language) -> ChatPromptTemplate:
        
        prompt: ChatPromptTemplate = hub.pull(self.prompt_name)
        # LANG not user for now
        # prompt = prompt.partial(language=lang.lang_name)
        return prompt