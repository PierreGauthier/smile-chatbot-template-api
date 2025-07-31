from fastapi import Depends

from config import Settings, get_settings
from ai import LlmProvider, AzureOpenAiLlmProvider, GCPVertexLlmProvider

def get_llm_agent(settings: Settings = Depends(get_settings)) -> LlmProvider:
    provider = settings.llm_provider.lower()

    match provider:
        case "azure":
            return AzureOpenAiLlmProvider(settings)
        case "gcp":
            return GCPVertexLlmProvider(settings)
        case _:
            raise ValueError(f"Unsupported LLM provider: {provider}")
