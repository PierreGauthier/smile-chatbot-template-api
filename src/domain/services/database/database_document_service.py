from abc import ABC, abstractmethod

from domain.models import RagDocument

class DatabaseDocumentService:

    @abstractmethod
    def get_document(self, doc_type:str, document_id:str) -> RagDocument:
        pass