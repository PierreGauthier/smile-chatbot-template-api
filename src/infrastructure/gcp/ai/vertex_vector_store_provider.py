# gcp_vectorstore_provider.py
from typing import Annotated

from fastapi import Depends
from langchain_core.vectorstores.base import BaseRetriever
from google.oauth2 import service_account
from langchain_google_vertexai.vectorstores import VectorSearchVectorStore

from ai import VectorStoreProvider, EmbeddingsProvider, OpenAIEmbeddingsProvider
from config import Settings, get_settings
from models import IndexFilterResult

class VertexVectorStoreProvider(VectorStoreProvider):
    """VectorStoreProvider that queries Vertex AI Vector Search and stores raw docs / metadata in GCS."""

    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        embeddings_provider: Annotated[EmbeddingsProvider, Depends(OpenAIEmbeddingsProvider)]):
        
        self.embeddings = embeddings_provider.get_embeddings()

        # GCP connection details pulled from your typed settings.
        self.project_id: str = settings.gcp_project_id
        self.region: str = settings.gcp_vertex_vector_location # e.g. "us-central1"
        self.index_endpoint_id: str = settings.gcp_vertex_vector_endpoint_id
        self.rag_k: int = settings.rag_k                    # top-K for retrieval
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.gcp_credentials_path
        )
        self.settings = settings

    def get_vector_store_as_retriever(self, index: IndexFilterResult) -> BaseRetriever:
        """Return a LangChain retriever backed by Vertex AI Vector Search."""

        vector_store:VectorSearchVectorStore = VectorSearchVectorStore.from_components(
            project_id=self.project_id,
            region=self.region,
            index_id=index.index_name,          
            embedding=self.embeddings,
            # Optional if you deploy multiple indexes behind one endpoint
            endpoint_id=self.index_endpoint_id,
            gcs_bucket_name=self.settings.gcp_storage_document_bucket_name,
            credentials=self.credentials
        )

        # Build the retriever with the same semantics as your Azure version.
        search_kwargs: dict = {"k": self.rag_k}

        # If you have per-query metadata filters, pass them as a filter string
        # that Vertex AI Vector Search understands, e.g. "author = 'alice'".
        if getattr(index, "filter", None):
            search_kwargs["filter"] = index.filter

        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.rag_k, **({"filter": index.filter} if getattr(index, "filter", None) else {})},
        )
