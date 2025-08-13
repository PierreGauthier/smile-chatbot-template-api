from fastapi import Depends

from config import Settings, get_settings
from ai import (
    LlmProvider, 
    AzureOpenAiLlmProvider, 
    GCPVertexLlmProvider, 
    EmbeddingsProvider, 
    OpenAIEmbeddingsProvider,
    VectorStoreProvider,
    GCPVertexVectorStoreProvider,
    AzureSearchVectorStoreProvider
)
from infrastructure.gcp.services import GoogleCloudStorageDocumentService, FirestoreHistoryService
from infrastructure.azure.services import CosmosDbDocumentService, CosmosDbHistoryService
from services import DatabaseHistoryService, DatabaseDocumentService

def inject_llm_provider(settings: Settings = Depends(get_settings)) -> LlmProvider:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return AzureOpenAiLlmProvider(settings)
        case "gcp":
            return GCPVertexLlmProvider(settings)
        case _:
            raise ValueError(f"Unsupported LLM provider: {provider}")

def inject_embedding_provider(settings: Settings = Depends(get_settings)) -> EmbeddingsProvider:
    return OpenAIEmbeddingsProvider(settings)

def inject_history_service(settings: Settings = Depends(get_settings)) -> DatabaseHistoryService:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return CosmosDbHistoryService(settings)
        case "gcp":
            return FirestoreHistoryService(settings)
        case _:
            raise ValueError(f"Unsupported History DB service provider: {provider}")
        
def inject_document_service(settings: Settings = Depends(get_settings)) -> DatabaseDocumentService:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return CosmosDbDocumentService(settings)
        case "gcp":
            return GoogleCloudStorageDocumentService(settings)
            #return FirestoreDocumentService(FirestoreDocumentDb(settings))
        case _:
            raise ValueError(f"Unsupported Document DB service provider: {provider}")
        
def inject_vector_store_provider(settings: Settings = Depends(get_settings)) -> VectorStoreProvider:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return AzureSearchVectorStoreProvider(
                settings=settings,
                embeddings_provider=OpenAIEmbeddingsProvider(settings)
            )
        case "gcp":
            return GCPVertexVectorStoreProvider(
                settings=settings,
                embeddings_provider=OpenAIEmbeddingsProvider(settings)
            )
        case _:
            raise ValueError(f"Unsupported vector store service provider: {provider}")