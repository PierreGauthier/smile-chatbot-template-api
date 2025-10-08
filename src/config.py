from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    project_name:str
    environment: str = "local"
    debug: bool = False
    log_level: str = "INFO"
    search_lang:str = "FR"
    llm_provider:str
    
    openai_api_version: str = "2020-05-10"
    openai_api_key: str

    azure_cosmos_url: str
    azure_cosmos_key: str
    azure_cosmos_database: str
    azure_cosmos_document_container: str
    azure_cosmos_document_partition_key: str
    azure_cosmos_history_container: str
    azure_cosmos_history_partition_key: str
    azure_cosmos_attributes_container:str
    azure_cosmos_attributes_partition_key:str
    azure_cosmos_filters_container:str
    azure_cosmos_filters_partition_key:str
    azure_cosmos_request_container:str
    azure_cosmos_request_partition_key:str
    
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
    pythonunbuffered:int
    
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
    langsmith_language_detector_prompt_name: str


    # Elastic suite
    langsmith_attribute_set_extraction_prompt_name:str
    langsmith_filters_extraction_prompt_name:str
    langsmith_elastic_suite_question_summarizer_prompt_name:str

    elastic_suite_api_base_url: str
    elastic_suite_attribute_set_endpoint:str
    elastic_suite_username:str
    elastic_suite_password:str
    # Search
    elastic_suite_search_api_base_url:str
    elastic_suite_search_api_credentials:str
    langsmith_empty_search_response_builder_prompt_name:str
    langsmith_not_empty_search_response_builder_prompt_name:str

    rag_k: int = 3
    rag_score_threshold: float = 0.8
    max_tokens: Optional[int] = 2048
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 40

    gcp_project_id:str
    gcp_credentials_path:str
    firestore_database_id: str
    firestore_document_collection:str
    firestore_history_collection:str
    gcp_vertex_model_name:str
    gcp_vertex_location:str
    gcp_vertex_temperature:str
    gcp_vertex_vector_location:str
    gcp_vertex_vector_index_id:str
    gcp_vertex_vector_endpoint_id:str
    gcp_storage_document_bucket_name:str
    gcp_storage_document_bucket_collection:str
        
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

#@lru_cache
def get_settings():
    return Settings()