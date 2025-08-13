from typing import Annotated
from fastapi import Depends
from langchain_google_vertexai import ChatVertexAI
from google.oauth2 import service_account

from config import Settings, get_settings
from ai import LlmProvider

class VertexLlmProvider(LlmProvider):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        credentials = None
        if settings.gcp_credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                settings.gcp_credentials_path
            )
        self.chat = ChatVertexAI(
            model_name=settings.gcp_vertex_model_name,
            project=settings.gcp_project_id,
            location=settings.gcp_vertex_location,
            credentials=credentials,
            temperature=settings.gcp_vertex_temperature,
            max_tokens=settings.max_tokens,
            top_p=settings.top_p,
            top_k=settings.top_k
        )
        
    def get_llm(self):
        return self.chat
    
    def invoke(self, messages):
        return self.chat.invoke(messages)