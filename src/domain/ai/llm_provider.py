from abc import ABC, abstractmethod

class LlmProvider(ABC):

    @abstractmethod
    def get_llm(self):
        pass

    @abstractmethod
    def invoke(self, messages):
        pass