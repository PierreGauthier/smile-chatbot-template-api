from fastapi import Depends
from typing import Annotated

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from config import Settings, get_settings
from domain.models import SearchContext
from application.prompts import StaticPromptProvider

class LangsmithChitChatPromptProvider(StaticPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_chit_chat_prompt_name


    def get_prompt(self, context: SearchContext = None) -> ChatPromptTemplate:
        """
        Retrieve and configure the chit-chat prompt.
        
        Args:
            context: Optional SearchContext to extract language information
            
        Returns:
            ChatPromptTemplate with language pre-filled if context provided
        """
        prompt: ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)
        
        # If context provided, inject the detected language
        if context and context.chat_lang:
            prompt = prompt.partial(output_language=context.chat_lang.lang_name)
        
        return prompt