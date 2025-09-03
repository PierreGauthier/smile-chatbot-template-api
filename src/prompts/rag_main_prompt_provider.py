from typing import List
from abc import ABC, abstractmethod

from langchain_core.prompts import ChatPromptTemplate

class RagMainPromptProvider(ABC):

    @abstractmethod
    def get_prompt(self, exchange:str, extra_info:List[str] = []) -> ChatPromptTemplate:
        pass