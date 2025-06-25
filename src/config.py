from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

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
    
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_deployment: str
    azure_openai_embedding_deployment: str
    azure_openai_temperature : float = 0.2

    max_history_size: int = 10
    max_history_token: int = 200

    microsoft_app_id: Optional[str] = None
    microsoft_app_password: Optional[str] = None

    azure_ad_client_id: Optional[str] = None
    azure_ad_tenant_id: Optional[str] = None

    applicationinsights_connection_string: Optional[str] = None
    cors_allowed_origins: Optional[str] = "*"
    
    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index: str
    
    langchain_api_key: str
    langsmith_contextualize_question_prompt_name: str
    langsmith_extract_request_definition_prompt_name : str
    langsmith_rag_system_prompt_name : str
    langsmith_summary_exchange_prompt_name: str
    langsmith_intent_extraction_prompt_name: str
    rag_k: int = 3
    rag_score_threshold: float = 0.8
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

#@lru_cache
def get_settings():
    return Settings()