from abc import ABC, abstractmethod

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from models import ElasticSuiteAttributeSet

class AttributeSetExtractionPromptProvider(ABC):

    @abstractmethod
    def get_prompt(
            self, 
            attribute_set:List[ElasticSuiteAttributeSet], 
            product_counter_example:str) -> ChatPromptTemplate:
        pass