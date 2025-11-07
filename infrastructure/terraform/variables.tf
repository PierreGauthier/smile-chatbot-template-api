variable "resource_group_name" {
    description = "Name of the resource group"
    type        = string
    default     = "maya-dev-rg"
}

variable "location" {
    description = "Azure region for resources"
    type        = string
    default     = "francecentral"
}

variable "app_service_name" {
    description = "Name of the App Service"
    type        = string
    default     = "maya-dev-api"
}

variable "python_version" {
    description = "Python version for the runtime"
    type        = string
    default     = "3.10"
}

# New variable for app settings
variable "app_settings" {
    description = "Application settings (environment variables) for the App Service"
    type        = map(string)
    default     = {
        "PROJECT_NAME" = "smile-chatbot-template"
		"LOG_LEVEL" = "DEBUG"
		"SEARCH_LANG" = "FR"
		"AZURE_COSMOS_DATABASE" = "chatbot"
		"AZURE_COSMOS_DOCUMENT_CONTAINER" = "embeddings"
		"AZURE_COSMOS_DOCUMENT_PARTITION_KEY" = "doc_type"
		"AZURE_COSMOS_HISTORY_CONTAINER" = "history"
		"AZURE_COSMOS_HISTORY_PARTITION_KEY" = "user_id"
		"AZURE_COSMOS_ATTRIBUTES_CONTAINER" = "attributes"
		"AZURE_COSMOS_ATTRIBUTES_PARTITION_KEY" = "project_id"
		"AZURE_COSMOS_FILTERS_CONTAINER" = "filters"
		"AZURE_COSMOS_FILTERS_PARTITION_KEY" = "attribute_id"
		"AZURE_COSMOS_REQUEST_CONTAINER" = "requests"
		"AZURE_COSMOS_REQUEST_PARTITION_KEY" = "user_id"
    }
}

variable "key_vault_name" {
    description = "Name of the Key Vault"
    type        = string
    default     = "maya-dev-kv"
}