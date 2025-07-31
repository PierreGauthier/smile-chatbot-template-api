from google.cloud import firestore
from google.oauth2 import service_account

from config import Settings

class FirestoreBase:
    def __init__(self, settings: Settings):
        self.project_id = settings.gcp_project_id
        self.credentials_path = settings.gcp_credentials_path
        self.collection_name = settings.firestore_document_collection
        self.database_id = settings.firestore_database_id
        self.client = self._get_firestore_client()
        
    def _get_firestore_client(self) -> firestore.Client:
        if self.credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            return firestore.Client(
                project=self.project_id, 
                credentials=credentials,
                database=self.database_id
            )
        else:
            # Use default credentials (e.g., when running on GCP)
            return firestore.Client(project=self.project_id, database=self.database_id)
    
    def get_collection(self) -> firestore.CollectionReference:
        return self.client.collection(self.collection_name)