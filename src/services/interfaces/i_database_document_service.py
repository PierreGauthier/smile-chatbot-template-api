from abc import ABC, abstractmethod

from models import VectorizedDocumentDto

class IDatabaseDocumentService:

    @abstractmethod
    def get_document(self, doc_type:str, document_id:str) -> VectorizedDocumentDto:
        pass
    
    @abstractmethod        
    def create_document_with_embedding(self, document:VectorizedDocumentDto) -> VectorizedDocumentDto:
        pass