from typing import Annotated
from fastapi import Depends

from config import Settings, get_settings
from models import RagDocument, RagDocumentMetadata
from services import DatabaseDocumentService
from infrastructure.gcp.services import Firestore

class FirestoreDocumentService(DatabaseDocumentService):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.database = Firestore(
            collection=settings.firestore_document_collection,
            settings=settings
        )
    
    def get_document(self, doc_type: str, document_id: str) -> RagDocument:
        collection_ref = self.database.get_collection()
        doc_ref = collection_ref.document(document_id)
        doc_snapshot = doc_ref.get()
        
        if not doc_snapshot.exists:
            raise ValueError(f"Document with ID {document_id} not found")
        
        document_data = doc_snapshot.to_dict()
        return self.__parse_document_data(document_data)
    
    def __parse_document_data(self, document: dict):
        metadata_dict = document['metadata']
        return RagDocument(
            content = document["content"],
            metadata=RagDocumentMetadata(
                id = document["id"],
                doc_type = document["doc_type"],
                sourceName = metadata_dict["sourceName"],
                contentType = metadata_dict["contentType"],
                pageNumber = metadata_dict["pageNumber"],
                documentUrl = metadata_dict["documentUrl"]
            )
        )
