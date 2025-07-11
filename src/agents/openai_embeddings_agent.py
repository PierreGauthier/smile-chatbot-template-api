from typing import Annotated
from fastapi import Depends
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from config import Settings, get_settings
from agents import EmbeddingsAgent

class OpenAIEmbeddingsAgent(EmbeddingsAgent):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

    def get_embeddings(self) -> Embeddings:
        return self.embeddings