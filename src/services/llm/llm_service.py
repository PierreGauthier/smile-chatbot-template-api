from abc import ABC, abstractmethod

class LlmService(ABC):
    @abstractmethod
    def get_llm(self):
        pass