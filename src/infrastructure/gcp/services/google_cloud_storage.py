from google.oauth2 import service_account
from google.cloud import storage

from config import Settings

class GoogleCloudStorage:
    def __init__(self, settings: Settings, bucket_name:str, bucket_collection:str):
        if getattr(settings, "gcp_credentials_path", None):
            # Build a GCS client (service account path optional; default credentials if running in GCP).
            credentials = service_account.Credentials.from_service_account_file(
                settings.gcp_credentials_path
            )
            self.client = storage.Client(project=settings.gcp_project_id, credentials=credentials)
        else:
            self.client = storage.Client(project=settings.gcp_project_id)
        self.bucket = self.client.bucket(bucket_name)
        self.collection = bucket_collection
    
    def get_blob(self, document_id:str):
        blob_name = f"{self.collection}/{document_id}"
        return (self.bucket.blob(blob_name), blob_name)