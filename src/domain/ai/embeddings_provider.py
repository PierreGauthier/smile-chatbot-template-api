from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class EmbeddingsProvider(ABC):
    """Contract for components that supply a ready-to-use LangChain `Embeddings` instance."""

    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass
