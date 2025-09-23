from abc import ABC, abstractmethod

from domain.models import Language

class LanguageDetector(ABC):

    @abstractmethod
    def detect_lang(self, message:str) -> Language:
        pass