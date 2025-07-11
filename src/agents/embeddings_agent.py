from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class EmbeddingsAgent(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass