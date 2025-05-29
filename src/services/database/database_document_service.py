from abc import ABC, abstractmethod

from models import VectorizedDocument

class DatabaseDocumentService:

    @abstractmethod
    def get_document(self, doc_type:str, document_id:str) -> VectorizedDocument:
        pass
    
    @abstractmethod        
    def create_document_with_embedding(self, document:VectorizedDocument) -> VectorizedDocument:
        pass