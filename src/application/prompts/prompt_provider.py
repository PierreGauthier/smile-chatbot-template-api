from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from langchain_core.prompts import ChatPromptTemplate

from domain.models import BaseContext

T = TypeVar('T', bound=BaseContext)

class PromptProvider(ABC, Generic[T]):
    """A prompt provider"""

    # @property  TODO pigau
    # # @abstractmethod
    # def prompt_name(self) -> str:
    #     return 'toto'

    @abstractmethod
    def get_prompt(self, context:T) -> ChatPromptTemplate:
        pass