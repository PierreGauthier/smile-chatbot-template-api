from fastapi import Depends

from config import Settings, get_settings
from ai import LlmProvider, AzureOpenAiLlmProvider, GCPVertexLlmProvider
from services import (
    DatabaseHistoryService, 
    CosmosDbHistoryService, 
    CosmosDbHistoryDb,
    FirestoreHistoryService,
    FirestoreHistoryDb
)

def get_llm_agent(settings: Settings = Depends(get_settings)) -> LlmProvider:
    provider = settings.llm_provider.lower()

    match provider:
        case "azure":
            return AzureOpenAiLlmProvider(settings)
        case "gcp":
            return GCPVertexLlmProvider(settings)
        case _:
            raise ValueError(f"Unsupported LLM provider: {provider}")

def get_history_service(settings: Settings = Depends(get_settings)) -> DatabaseHistoryService:
    provider = settings.llm_provider.lower()

    match provider:
        case "azure":
            return CosmosDbHistoryService(CosmosDbHistoryDb(settings))
        case "gcp":
            return FirestoreHistoryService(FirestoreHistoryDb(settings))
        case _:
            raise ValueError(f"Unsupported History service provider: {provider}")