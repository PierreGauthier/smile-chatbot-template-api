from abc import ABC, abstractmethod
from typing import List

from langchain_core.prompts import ChatPromptTemplate

from models import AttributeFilterDto

class FiltersExtractionPromptProvider(ABC):

    @abstractmethod
    def get_prompt(self, filters:List[AttributeFilterDto]) -> ChatPromptTemplate:
        pass