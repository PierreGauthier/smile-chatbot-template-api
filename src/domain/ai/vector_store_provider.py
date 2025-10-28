from abc import ABC, abstractmethod
from langchain_core.vectorstores.base import BaseRetriever

from domain.models import IndexFilterResult

class VectorStoreProvider(ABC):
    """Interface for resolving a vector store retriever for a given index."""

    @abstractmethod
    def get_vector_store_as_retriever(self, index: IndexFilterResult) -> BaseRetriever:
        pass
    
