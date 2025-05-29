from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class EmbeddingsService(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass