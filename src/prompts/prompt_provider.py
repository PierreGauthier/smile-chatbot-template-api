from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate

class PromptProvider(ABC):
    @abstractmethod
    def get_prompt(self) -> ChatPromptTemplate:
        pass