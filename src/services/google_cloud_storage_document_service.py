from typing import Annotated
from fastapi import Depends
from typing import Annotated
from fastapi import Depends
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.exceptions import NotFound
from langchain_core.documents import Document
import json

from config import Settings, get_settings

from models import VectorizedDocument, GoogleCloudStorageDocumentMapper
from services import DatabaseDocumentService, FirestoreBase, FirestoreDocumentDb

class GoogleCloudStorageDocumentService(DatabaseDocumentService):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings
        # Build a GCS client (service account path optional; default credentials if running in GCP).
        if getattr(settings, "gcp_credentials_path", None):
            credentials = service_account.Credentials.from_service_account_file(
                settings.gcp_credentials_path
            )
            self.client = storage.Client(project=settings.gcp_project_id, credentials=credentials)
        else:
            self.client = storage.Client(project=settings.gcp_project_id)
        self.bucket = self.client.bucket(self.settings.gcp_storage_document_bucket_name)
    
    def get_document(self, doc_type: str, document_id: str) -> VectorizedDocument:
        blob_name = f"{self.settings.gcp_storage_document_bucket_collection}/{document_id}"
        blob = self.bucket.blob(blob_name)

        try:
            raw_data = blob.download_as_text()  # raises NotFound if missing
        except NotFound:
            return None

        try:
            document_data = json.loads(raw_data)
            return GoogleCloudStorageDocumentMapper.from_dict(document_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in GCS object {blob_name}: {e}") from e

    def create_document_with_embedding(self, document: VectorizedDocument) -> VectorizedDocument:
        return None