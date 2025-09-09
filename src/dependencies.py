import logging, sys, os
from fastapi import Depends
from langchain_core.prompts import ChatPromptTemplate

from config import Settings, get_settings
from ai import LlmProvider, EmbeddingsProvider, OpenAIEmbeddingsProvider, VectorStoreProvider
from api_clients import ConversationalSearchClient
from infrastructure.gcp.services import GoogleCloudStorageDocumentService, FirestoreHistoryService
from infrastructure.gcp.ai import VertexLlmProvider, VertexVectorStoreProvider
from infrastructure.azure.services import (
    CosmosDbDocumentService, 
    CosmosDbHistoryService, 
    CosmosDBAttributesSetupService,
    CosmosDbRequestService
)
from infrastructure.azure.ai import AzureOpenAiLlmProvider, AzureSearchVectorStoreProvider
from services import (
    DatabaseHistoryService, 
    DatabaseDocumentService, 
    DatabaseAttributesSetupService, 
    DatabaseRequestService
)
from infrastructure.search.elastic_suite import ElasticSuiteSearchClient, ElasticSuiteSearchResponseBuilder
from infrastructure.prompts.langsmith import (
    LangsmithAttributeSetExtractionPromptProvider,
    LangsmithFiltersExtractionPromptProvider,
    LangsmithIntentExtractionPromptProvider,
    LangsmithQuestionSummarizerPromptProvider,
    LangsmithRagMainPromptProvider,
    LangsmithSearchResponseBuilderPromptProvider,
    LangsmithEmptySearchResponseBuilderPromptProvider,
    LangsmithExchangeSummarizerPromptProvider
)
from logger import ContextLogger

settings = get_settings()

logger = logging.getLogger("app")
logger.setLevel(logging.INFO if settings.log_level == "INFO" else logging.DEBUG)
object_logger = ContextLogger(logger, {"component": "C-Search"})

def inject_logger() -> ContextLogger:
    return object_logger

def inject_embedding_provider(settings: Settings = Depends(get_settings)) -> EmbeddingsProvider:
    return OpenAIEmbeddingsProvider(settings)

def inject_llm_provider(settings: Settings = Depends(get_settings)) -> LlmProvider:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return AzureOpenAiLlmProvider(settings)
        case "gcp":
            return VertexLlmProvider(settings)
        case _:
            raise ValueError(f"Unsupported LLM provider: {provider}")

def inject_attribute_database_service(settings: Settings = Depends(get_settings)) -> DatabaseAttributesSetupService:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return CosmosDBAttributesSetupService(settings)
        case _:
            raise ValueError(f"Unsupported History DB service provider: {provider}")

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
        
def inject_request_service(settings: Settings = Depends(get_settings)) -> DatabaseRequestService:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return CosmosDbRequestService(settings)
        case _:
            raise ValueError(f"Unsupported Request DB service provider: {provider}")
        
def inject_vector_store_provider(settings: Settings = Depends(get_settings)) -> VectorStoreProvider:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return AzureSearchVectorStoreProvider(
                settings=settings,
                embeddings_provider=OpenAIEmbeddingsProvider(settings)
            )
        case "gcp":
            return VertexVectorStoreProvider(
                settings=settings,
                embeddings_provider=OpenAIEmbeddingsProvider(settings)
            )
        case _:
            raise ValueError(f"Unsupported vector store service provider: {provider}")

def inject_conversational_search_api(settings: Settings = Depends(get_settings)) -> ConversationalSearchClient:
    return ElasticSuiteSearchClient(settings, ElasticSuiteSearchResponseBuilder())

# PROMPTS

def inject_attribute_set_extraction_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithAttributeSetExtractionPromptProvider(settings)

def inject_filters_extraction_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithFiltersExtractionPromptProvider(settings)

def inject_intent_extraction_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithIntentExtractionPromptProvider(settings)

def inject_question_summarizer_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithQuestionSummarizerPromptProvider(settings)

def inject_rag_main_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithRagMainPromptProvider(settings)

def inject_search_response_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithSearchResponseBuilderPromptProvider(settings)

def inject_empty_search_response_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithEmptySearchResponseBuilderPromptProvider(settings)

def inject_exchange_summarizer_prompt(settings: Settings = Depends(get_settings)) -> ChatPromptTemplate:
    return LangsmithExchangeSummarizerPromptProvider(settings)
