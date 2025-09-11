from abc import ABC, abstractmethod
from typing import List

from langchain_core.prompts import ChatPromptTemplate

from domain.models import ChatMessage

class QuestionSummarizerPromptProvider(ABC):

    @abstractmethod
    def get_prompt(self, exchange:List[ChatMessage]) -> ChatPromptTemplate:
        pass
