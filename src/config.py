import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from pydantic.fields import FieldInfo
from typing import Any, Dict, Mapping, Optional, Tuple, Type
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.appconfiguration.provider import load, SettingSelector

class Settings(BaseSettings):
    project_name:str
    environment: str = "local"
    debug: bool = False
    
    openai_api_version: str = "2020-05-10"
    openai_api_key: str

    azure_cosmos_url: str
    azure_cosmos_key: str
    azure_cosmos_database: str
    azure_cosmos_document_container: str
    azure_cosmos_document_partition_key: str
    azure_cosmos_history_container: str
    azure_cosmos_history_partition_key: str
    azure_cosmos_request_container:str
    azure_cosmos_request_partition_key:str
    
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_deployment: str
    azure_openai_embedding_deployment: str
    azure_openai_temperature : float = 0.2

    bot_welcome_message: str = "Hello and welcome!"
    bot_error_message: str = "Oops something went wrong!"
    prompt_system: str = "You are a helpful assistant. Answer all questions to the best of your ability."
    max_history_size: int = 10
    max_history_token: int = 200

    microsoft_app_id: Optional[str] = None
    microsoft_app_password: Optional[str] = None

    azure_ad_client_id: Optional[str] = None
    azure_ad_tenant_id: Optional[str] = None

    applicationinsights_connection_string: Optional[str] = None
    cors_allowed_origins: Optional[str] = None
    
    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index: str
    
    langchain_api_key: str
    langsmith_contextualize_question_prompt_name: str
    langsmith_extract_request_definition_prompt_name : str
    langsmith_rag_system_prompt_name : str
    langsmith_summary_exchange_prompt_name: str
    contextualize_question_system_prompt: str = """Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone question
    which can be understood without the chat history. Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is."""
    rag_system_prompt: str = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

    {context}"""
    rag_k: int = 3
    rag_score_threshold: float = 0.8
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

#@lru_cache
def get_settings():
    return Settings()