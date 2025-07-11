from typing import Annotated
from fastapi import Depends
from langchain_openai import AzureChatOpenAI

from config import Settings, get_settings
from agents import LlmAgent

class AzureOpenAiLlmAgent(LlmAgent):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.chat = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            openai_api_key=settings.azure_openai_api_key,
            openai_api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_deployment,
            temperature=settings.azure_openai_temperature)
        
    def get_llm(self):
        return self.chat
    
    def invoke(self, messages):
        return self.chat.invoke(messages)