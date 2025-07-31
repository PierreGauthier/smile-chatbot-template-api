from typing import Annotated
from fastapi import Depends
import uuid

from models import VectorizedDocument
from services import DatabaseDocumentService, FirestoreBase, FirestoreDocumentDb

class FirestoreDocumentService(DatabaseDocumentService):
    def __init__(self, database: Annotated[FirestoreBase, Depends(FirestoreDocumentDb)]):
        self.database = database
    
    def get_document(self, doc_type: str, document_id: str) -> VectorizedDocument:
        collection_ref = self.database.get_collection()
        doc_ref = collection_ref.document(document_id)
        doc_snapshot = doc_ref.get()
        
        if not doc_snapshot.exists:
            raise ValueError(f"Document with ID {document_id} not found")
        
        document_data = doc_snapshot.to_dict()
        return VectorizedDocument.from_dict(document_data)
    
    def create_document_with_embedding(self, document: VectorizedDocument) -> VectorizedDocument:
        collection_ref = self.database.get_collection()
        
        doc_id = str(uuid.uuid4())
        doc_data = {
            "id": doc_id,
            "doc_type": document.metadata.contentType,
            "content": document.content,
            "content_vector": document.content_vector,
            "metadata": document.metadata.to_dict()
        }
        
        # Create document with generated ID
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(doc_data)
        
        # Update the document ID and return
        document.id = doc_id
        return document
