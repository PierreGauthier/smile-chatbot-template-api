from abc import ABC, abstractmethod
from langchain_core.vectorstores.base import VectorStore, BaseRetriever

from models import IndexFilterResult

class IVectorStoreService(ABC):

    @abstractmethod
    def get_vector_store_as_retriever(self, index: IndexFilterResult) -> BaseRetriever:
        pass
    