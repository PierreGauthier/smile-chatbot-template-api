from abc import ABC, abstractmethod

from domain.models import Language, BaseContext

class LanguageDetector(ABC):
    """Contract for components that infer the language of a user message."""

    @abstractmethod
    def detect_lang(self, message: str, context:BaseContext) -> Language:
        pass
