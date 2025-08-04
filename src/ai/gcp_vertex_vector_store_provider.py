# gcp_vectorstore_provider.py
from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from langchain_core.vectorstores.base import BaseRetriever

# LangChain Google Vertex AI integration  (pip install langchain-google-vertexai>=0.1.0)
from langchain_google_vertexai.vectorstores import MatchingEngine

from ai import (
    VectorStoreProvider,            # your base ABC
    EmbeddingsProvider,             # generic interface
    OpenAIEmbeddingsProvider        # or a VertexAIEmbeddingsProvider you already have
)
from config import Settings, get_settings
from models import IndexFilterResult


class GCPVertexVectorStoreProvider(VectorStoreProvider):
    """VectorStoreProvider that queries Vertex AI Vector Search and stores
    raw docs / metadata in Firestore (not shown here)."""

    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        embeddings_agent: Annotated[
            EmbeddingsProvider, Depends(OpenAIEmbeddingsProvider)
        ],
    ):
        # Any embeddings model is fine as long as the same vectors were
        # up-loaded into Vertex AI (OpenAI, Gecko, custom, etc.).
        self.embeddings = embeddings_agent.get_embeddings()

        # GCP connection details pulled from your typed settings.
        self.project_id: str = settings.gcp_project_id
        self.region: str = settings.gcp_vertex_location # e.g. "us-central1"
        self.index_endpoint_id: str | None = getattr(
            settings, "vertex_index_endpoint_id", None
        )                                                   # optional
        self.rag_k: int = settings.rag_k                    # top-K for retrieval

    # --------------------------------------------------------------------- #
    # VectorStoreProvider interface
    # --------------------------------------------------------------------- #
    def get_vector_store_as_retriever(              # noqa: D401
        self, index: IndexFilterResult
    ) -> BaseRetriever:
        """Return a LangChain retriever backed by Vertex AI Vector Search."""

        # 1️⃣  Construct the LangChain vector store wrapper.
        #
        # `index.index_name` is assumed to hold the Vertex AI Vector Search
        # *index ID* (the numeric string). If you prefer, extend your
        # IndexFilterResult to expose `index_id` explicitly.
        vector_store = MatchingEngine.from_components(
            project_id=self.project_id,
            region=self.region,
            index_id=index.index_name,
            embedding=self.embeddings,
            # Optional if you deploy multiple indexes behind one endpoint
            index_endpoint_id=self.index_endpoint_id,
        )

        # 2️⃣  Build the retriever with the same semantics as your Azure version.
        search_kwargs: dict = {"k": self.rag_k}

        # If you have per-query metadata filters, pass them as a filter string
        # that Vertex AI Vector Search understands, e.g. "author = 'alice'".
        if getattr(index, "filter", None):
            search_kwargs["filter"] = index.filter

        return vector_store.as_retriever(
            search_type="similarity",   # or "mmr" if you prefer
            search_kwargs=search_kwargs,
        )
