from typing import Annotated
from fastapi import Depends
from langchain_ollama.chat_models import ChatOllama

from domain.ai import LlmProvider

from config import Settings, get_settings

class OllamaLlmProvider(LlmProvider):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.chat = ChatOllama(
            model="gemma3",
            temperature=0.1
        )
        
    def get_llm(self):
        return self.chat
    
    def invoke(self, messages):
        return self.chat.invoke(messages)
