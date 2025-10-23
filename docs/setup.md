# Installation

Install Python environments:

```bash
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-ipykernel
sudo apt install python3-venv
sudo apt install python3-dotenv
```

Install required packages using `requirements.txt` file.

**Crtl+Shift-P** > *Python: Create Environment*

- Select Python installation (3.10.x)
- Select the requirements file
- Delete and recreate existing environment

# Configuration

At start-up, the project loads a set of configurations from different sources (environment variables, configuration files, etc.).

The different sources are loaded following a predefined order. If a configuration is present in more than one source, the last is taken into account:

## Sources order

1. File .env (only dev local)
2. Environment variables
3. Azure app configuration (empty label)
4. Azure app configuration (label == environment)

## Used configurations

| Key | Type | Secret | Description | Default values |
|-|-|-|-|-|
|PROJECT_NAME|str| |None| |
|ENVIRONMENT|str| |Execution environment|`local`|
|DEBUG|bool| |Langchain debug level|`False`|
|LOG_LEVEL|str| |General log level|`INFO`|
|SEARCH_LANG|str| |Preferred language for the conversational search|`FR`|
|LLM_PROVIDER|str| |Name of the infrastructure for LLMaaS| |
|OPENAI_API_VERSION|str| |OpenAI API version|`2020-05-10`|
|OPENAI_API_KEY|str|X|OpenAI API key| |
|AZURE_COSMOS_URL|str| |Cosmos DB Endpoint| |
|AZURE_COSMOS_KEY|str|X|Cosmos DB key| |
|AZURE_COSMOS_DATABASE|str| |Database name|`chatbot`|
|AZURE_COSMOS_DOCUMENT_CONTAINER|str| |Container name for content and embeddings (vectors)|`embeddings`|
|AZURE_COSMOS_DOCUMENT_PARTITION_KEY|str| |Document container's partition key|`doc_type`|
|AZURE_COSMOS_HISTORY_CONTAINER|str| |Container name for history (chat memory)|`history`|
|AZURE_COSMOS_HISTORY_PARTITION_KEY|str| |Container history's partition key|`user_id`|
|AZURE_COSMOS_ATTRIBUTES_CONTAINER|str| |Container name for attributes (search)|`attributes`|
|AZURE_COSMOS_ATTRIBUTES_PARTITION_KEY|str| |Container attribute's partition key|`project_id`|
|AZURE_COSMOS_FILTERS_CONTAINER|str| |Container name for filters (search)|`filters`|
|AZURE_COSMOS_FILTERS_PARTITION_KEY|str| |Container filter's partition key|`attribute_id`|
|AZURE_COSMOS_REQUEST_CONTAINER|str| |Container name for the requests (filters structure and detected values)|`requests`|
|AZURE_COSMOS_REQUEST_PARTITION_KEY|str| |Container request's partition key|`user_id`|
|AZURE_OPENAI_ENDPOINT|str| |Azure OpenAI endpoint| |
|AZURE_OPENAI_API_KEY|str|X|Azure OpenAI key| |
|AZURE_OPENAI_API_VERSION|str| |Azure OpenAI API version| |
|AZURE_OPENAI_DEPLOYMENT|str| |Azure OpenAI deployment name for completion (model)| |
|AZURE_OPENAI_EMBEDDING_DEPLOYMENT|str| |Azure OpenAI deployment name for embeddings (model)| |
|AZURE_OPENAI_TEMPERATURE|float| |# Azure OpenAI model temperature|`0.2`|
|MAX_HISTORY_SIZE|int| |History memory size|`10`|
|MAX_HISTORY_TOKEN|int| |maximum of history tokens|`200`|
|MICROSOFT_APP_ID|Optional[str]| |None|`None`|
|MICROSOFT_APP_PASSWORD|Optional[str]|X|None|`None`|
|AZURE_AD_CLIENT_ID|Optional[str]| |None|`None`|
|AZURE_AD_TENANT_ID|Optional[str]| |None|`None`|
|APPLICATIONINSIGHTS_CONNECTION_STRING|Optional[str]|X|App Insights connection string|`None`|
|PYTHONUNBUFFERED|int| |None|`1`|
|CORS_ALLOWED_ORIGINS|Optional[str]| |CORS configuration|`*`|
|AZURE_SEARCH_ENDPOINT|str| |Azure AI Search endpoint| |
|AZURE_SEARCH_KEY|str|X|Azure AI Search key| |
|AZURE_SEARCH_INDEX|str| |Azure AI Search default index name| |
|LANGCHAIN_API_KEY|str|X|Langchain API key| |
|LANGSMITH_CONTEXTUALIZE_QUESTION_PROMPT_NAME|str| |Name of the prompt for contextualizing messages| |
|LANGSMITH_EXTRACT_REQUEST_DEFINITION_PROMPT_NAME|str| |Name of the prompt for extracting a structured request| |
|LANGSMITH_RAG_SYSTEM_PROMPT_NAME|str| |Name of the main system prompt for RAG| |
|LANGSMITH_SUMMARY_EXCHANGE_PROMPT_NAME|str| |Name of the prompt for message history summarization| |
|LANGSMITH_INTENT_EXTRACTION_PROMPT_NAME|str| |Name of the prompt for intent detection| |
|LANGSMITH_LANGUAGE_DETECTOR_PROMPT_NAME|str| |Name of the prompt for language detection| |
|LANGSMITH_ATTRIBUTE_SET_EXTRACTION_PROMPT_NAME|str| |Name of the prompt for attribute extraction from user request| |
|LANGSMITH_FILTERS_EXTRACTION_PROMPT_NAME|str| |Name of the prompt for filters extraction from a user request| |
|LANGSMITH_ELASTIC_SUITE_QUESTION_SUMMARIZER_PROMPT_NAME|str| |Name of the prompt for user question summarization| |
|LANGSMITH_EMPTY_SEARCH_RESPONSE_BUILDER_PROMPT_NAME|str| |Name of the prompt for empty response (no product found) generation| |
|LANGSMITH_NOT_EMPTY_SEARCH_RESPONSE_BUILDER_PROMPT_NAME|str| |Name of the prompt for NOT empty response (some product found) generation| |
|ELASTIC_SUITE_API_BASE_URL|str| |Base URL for Elastic Suite attributes and filter retrieval| |
|ELASTIC_SUITE_ATTRIBUTE_SET_ENDPOINT|str| |Elastic Suite endpoint| |
|ELASTIC_SUITE_USERNAME|str| |Elastic Suite API username| |
|ELASTIC_SUITE_PASSWORD|str|X|Elastic Suite API password| |
|ELASTIC_SUITE_SEARCH_API_BASE_URL|str| |Elastic Suite search API base URL| |
|ELASTIC_SUITE_SEARCH_API_CREDENTIALS|str|X|Elastic Suite search API credentials| |
|RAG_K|int| |None|`3`|
|RAG_SCORE_THRESHOLD|float| |None|`0.8`|
|MAX_TOKENS|Optional[int]| |None|`2048`|
|TOP_P|Optional[float]| |None|`0.95`|
|TOP_K|Optional[int]| |None|`40`|
|GCP_PROJECT_ID|str| |GCP project ID| |
|GCP_CREDENTIALS_PATH|str| |GCP credential file path| |
|FIRESTORE_DATABASE_ID|str| |GCP Firestore database ID| |
|FIRESTORE_DOCUMENT_COLLECTION|str| |GCP Firestore document collection name|`documents`|
|FIRESTORE_HISTORY_COLLECTION|str| |GCP Firestore history collection name|`chat_history`|
|GCP_VERTEX_MODEL_NAME|str| |GCP Vertex model name| |
|GCP_VERTEX_LOCATION|str| |GCP Vertex location (region)| |
|GCP_VERTEX_TEMPERATURE|str| |None| |
|GCP_VERTEX_VECTOR_LOCATION|str| |GCP Vertex Vector Search location| |
|GCP_VERTEX_VECTOR_INDEX_ID|str| |GCP Vertex Vector Search default index ID| |
|GCP_VERTEX_VECTOR_ENDPOINT_ID|str| |GCP Vertex Vector Search endpoint| |
|GCP_STORAGE_DOCUMENT_BUCKET_NAME|str| |GCP GCS bucket name| |
|GCP_STORAGE_DOCUMENT_BUCKET_COLLECTION|str| |GCP GCS bucket collection name (for content)|`documents`|

# Launch

The file `launch.json` allows to run the application only by pressing `F5`.