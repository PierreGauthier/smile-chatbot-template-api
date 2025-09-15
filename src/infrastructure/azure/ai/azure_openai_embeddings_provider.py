from typing import Annotated
from fastapi import Depends
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureOpenAIEmbeddings

from domain.ai import EmbeddingsProvider

from config import Settings, get_settings

class AzureOpenAIEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=settings.azure_openai_embedding_deployment,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key
        )

    def get_embeddings(self) -> Embeddings:
        return self.embeddings