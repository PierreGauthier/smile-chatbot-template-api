import json
from typing import Annotated
from fastapi import Depends
from google.cloud.exceptions import NotFound

from config import Settings, get_settings

from models import RagDocument, RagDocumentMetadata
from services import DatabaseDocumentService
from infrastructure.gcp.services import GoogleCloudStorage

class GoogleCloudStorageDocumentService(DatabaseDocumentService):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.database = GoogleCloudStorage(
            settings=settings,
            bucket_name=settings.gcp_storage_document_bucket_name,
            bucket_collection=settings.gcp_storage_document_bucket_collection)
    
    def get_document(self, doc_type: str, document_id: str) -> RagDocument:
        (blob, blob_name) = self.database.get_blob(document_id)

        try:
            raw_data = blob.download_as_text()  # raises NotFound if missing
        except NotFound:
            return None

        try:
            document_data = json.loads(raw_data)
            return self.__parse_document_data(document_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in GCS object {blob_name}: {e}") from e
        
    def __parse_document_data(self, document: dict):
        metadata_dict = document['metadata']  
        return RagDocument(
            content = document["page_content"],
            metadata = RagDocumentMetadata(
                id=metadata_dict["id"],
                doc_type=metadata_dict["contentType"],
                sourceName=metadata_dict["sourceName"],
                contentType=document['metadata']["contentType"],
                pageNumber=document['metadata']["pageNumber"],
                documentUrl=document['metadata']["documentUrl"],
            )
        )