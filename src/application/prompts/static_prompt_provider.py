from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate

class StaticPromptProvider(ABC):
    """A prompt that needs no parameters"""
    
    @abstractmethod
    def get_prompt(self) -> ChatPromptTemplate:
        pass