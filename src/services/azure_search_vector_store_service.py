from typing import Annotated
from fastapi import Depends
from langchain_community.vectorstores.azuresearch import AzureSearch, AzureSearchVectorStoreRetriever
from config import Settings, get_settings

from services import OpenAIEmbeddingsService, EmbeddingsService, VectorStoreService
from models import IndexFilterResult
    
class AzureSearchVectorStoreService(VectorStoreService):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        embeddings_service: Annotated[EmbeddingsService, Depends(OpenAIEmbeddingsService)]):
        self.embeddings = embeddings_service.get_embeddings()
        self.azure_search_endpoint = settings.azure_search_endpoint
        self.azure_search_key = settings.azure_search_key
        self.rag_k = settings.rag_k
    
    def get_vector_store_as_retriever(self, index: IndexFilterResult) -> AzureSearchVectorStoreRetriever:
        vector_store = AzureSearch(
            azure_search_endpoint=self.azure_search_endpoint,
            azure_search_key=self.azure_search_key,
            index_name=index.index_name,
            embedding_function=self.embeddings.embed_query,
            semantic_configuration_name="basic_semantic_config"
        )
        return AzureSearchVectorStoreRetriever(vectorstore=vector_store, k=self.rag_k, search_type="semantic_hybrid") if not index.scoring_profile else \
        AzureSearchVectorStoreRetriever(vectorstore=vector_store, k=self.rag_k, search_type="semantic_hybrid", search_kwargs={
            "scoring_profile": index.scoring_profile.name,
            "scoring_parameters": [f"{index.scoring_profile.param_name}:{index.scoring_profile.param_value}"]
        })
