from abc import ABC, abstractmethod

class LlmAgent(ABC):

    @abstractmethod
    def get_llm(self):
        pass

    @abstractmethod
    def invoke(self, messages):
        pass