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

| Key | Type | Secret | Location | Description | Default values |
|-|-|-|-|-|-|
| ENVIRONMENT | string | | - | Execution environment |`Development`, `Staging`, `Production` |
| OPENAI_API_VERSION | string | | App Settings | OpenAI API version | `2023-05-15` |
| OPENAI_API_KEY | string | X | Key Vault (via App Settings) | OpenAI account key | |
| AZURE_COSMOS_URL | string | | App Settings | CosmosDB endpoint | |
| AZURE_COSMOS_KEY | string | X | Key Vault (via App Settings) | CosmosDB account key| |
| AZURE_COSMOS_DATABASE | string | | App Settings | CosmosDB database name | `chatbot`|
| AZURE_COSMOS_DOCUMENT_CONTAINER | string | | App Settings | Documents (embeddings) container name | `embeddings` |
| AZURE_COSMOS_DOCUMENT_PARTITION_KEY | string | | App Settings | Documents partition key | `doc_type` | 
| AZURE_COSMOS_HISTORY_CONTAINER | string| | App Settings | Message historization container name | `history` |
| AZURE_COSMOS_HISTORY_PARTITION_KEY | string | | App Settings | Message historization partition key | `user_id` | 
| AZURE_COSMOS_REQUEST_CONTAINER | string| | App Settings | Request historization container name | `request` |
| AZURE_COSMOS_REQUEST_PARTITION_KEY | string | | App Settings | Request historization partition key | `user_id` | 
| AZURE_OPENAI_ENDPOINT | string | | App Settings | Azure OpenAI endpoint | | 
| AZURE_OPENAI_API_KEY | string | X | Key Vault (via App Settings) | Azure OpenAI account key | | 
| AZURE_OPENAI_API_VERSION | string | | App Settings | Azure OpenAI API version | `2023-06-01-preview`|
| AZURE_OPENAI_DEPLOYMENT | string | | App Settings | Azure OpenAI LLM deployment name | `gpt-4o-mini` |
| AZURE_OPENAI_EMBEDDING_DEPLOYMENT | string | | App Settings | Azure OpenAI deployment name for embeddings | |
| AZURE_OPENAI_TEMPERATURE | float | | App Settings | LLM temperature | `0.2` |
| MAX_HISTORY_SIZE | int | | App Settings | Maximum number of history messages in the context| `10` |
| MAX_HISTORY_TOKEN | int | | App Settings | Maximum number of tokens in the history context | `500` |
| AZURE_SEARCH_ENDPOINT | string | | App Settings | Azure Search service endpoint | | 
| AZURE_SEARCH_KEY | string | X | Key Vault (via App Settings) | Azure Search account key | | 
| AZURE_SEARCH_INDEX | string | | App Settings | Name of the Azure Search index to use for document vectorial search | `main_rag_index`|
| RAG_K | int | | App Settings | Number of retrieved documents | `3` | 
| RAG_SCORE_THRESHOLD | float | | App Settings | Confidence threshold at which a document is accepted as relevant by Azure AI Search | `0.8` |
| LANGCHAIN_API_KEY | string | X | Key Vault (via App Settings) | LangSmith account key | |
| LANGSMITH_CONTEXTUALIZE_QUESTION_PROMPT_NAME | string | | App Settings | Name of LangSmith system prompt for contextualizing questions | | 
| LANGSMITH_EXTRACT_REQUEST_DEFINITION_PROMPT_NAME | string | | App Settings | Name of LangSmith system prompt for request information extraction | | 
| LANGSMITH_RAG_SYSTEM_PROMPT_NAME | string | | App Settings | Name of LangSmith system prompt for RAG | | 
| CONTEXTUALIZE_QUESTION_SYSTEM_PROMPT | string | | App Settings | System prompt for contextualizing questions | | 
| RAG_SYSTEM_PROMPT | string | | App Settings | System prompt for RAG | | 

# Launch

The file `launch.json` allows to run the application only by pressing `F5`.