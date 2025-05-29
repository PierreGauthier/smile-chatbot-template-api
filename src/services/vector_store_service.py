from abc import ABC, abstractmethod
from langchain_core.vectorstores.base import BaseRetriever

from models import IndexFilterResult

class VectorStoreService(ABC):

    @abstractmethod
    def get_vector_store_as_retriever(self, index: IndexFilterResult) -> BaseRetriever:
        pass
    