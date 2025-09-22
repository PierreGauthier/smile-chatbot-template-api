import logging, sys, os
from fastapi import Depends
from langchain_core.prompts import ChatPromptTemplate

from domain.logger import ContextLogger
from domain.ai import LlmProvider, EmbeddingsProvider, VectorStoreProvider
from domain.api_client import ConversationalSearchClient
from domain.services.database import (
    DatabaseHistoryService, 
    DatabaseDocumentService, 
    DatabaseAttributesSetupService, 
    DatabaseRequestService
)

# Avoid circular dependency injection
from application.agents.search_response_builder_agent import SearchResponseBuilderAgent
from application.models import RagChatMessage, SearchChatMessage

from infrastructure.gcp.services import GoogleCloudStorageDocumentService, FirestoreHistoryService
from infrastructure.gcp.ai import VertexLlmProvider, VertexVectorStoreProvider
from infrastructure.azure.services import (
    CosmosDbDocumentService, 
    CosmosDbHistoryService, 
    CosmosDBAttributesSetupService,
    CosmosDbRequestService
)
from infrastructure.azure.ai import AzureOpenAiLlmProvider, AzureSearchVectorStoreProvider
from infrastructure.openai.ai import OpenAIEmbeddingsProvider
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
from infrastructure.configuration.elastic_suite import ElasticSuiteAttributeSetClient, ElasticSuiteAttributeSetResponseBuilder
from infrastructure.agents.elastic_suite import ElasticSuiteSearchResponseBuilderAgent

from config import Settings, get_settings

settings = get_settings()

logger = logging.getLogger("app")
logger.setLevel(logging.INFO if settings.log_level == "INFO" else logging.DEBUG)

def inject_logger(module_name:str) -> ContextLogger:
    return ContextLogger(logger, {"component": module_name})

def inject_configuration_client(settings: Settings = Depends(get_settings)) -> ElasticSuiteAttributeSetClient:
    return ElasticSuiteAttributeSetClient(
        settings=settings,
        attribute_set_response_builder=ElasticSuiteAttributeSetResponseBuilder()
    )

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

def inject_history_service_for_RAG(settings: Settings = Depends(get_settings)) -> DatabaseHistoryService:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return CosmosDbHistoryService[RagChatMessage](RagChatMessage, settings)
        case "gcp":
            return FirestoreHistoryService[RagChatMessage](RagChatMessage, settings)
        case _:
            raise ValueError(f"Unsupported History DB service provider: {provider}")

def inject_history_service_for_search(settings: Settings = Depends(get_settings)) -> DatabaseHistoryService:
    provider = settings.llm_provider.lower()
    match provider:
        case "azure":
            return CosmosDbHistoryService[SearchChatMessage](SearchChatMessage, settings)
        case "gcp":
            return FirestoreHistoryService[SearchChatMessage](SearchChatMessage, settings)
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
    return ElasticSuiteSearchClient(
        settings, 
        ElasticSuiteSearchResponseBuilder(), 
        inject_logger(module_name="ElasticSuiteSearchClient")
    )

def inject_search_response_agent(settings: Settings = Depends(get_settings)) -> SearchResponseBuilderAgent:
    return ElasticSuiteSearchResponseBuilderAgent(
        settings=settings, 
        llm_provider=inject_llm_provider(settings),
        empty_search_prompt_provider=inject_empty_search_response_prompt(settings),
        not_empty_search_prompt_provider=inject_search_response_prompt(settings)
    )

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
