output "resource_group_name" {
  description = "Name of the Resource Group"
  value       = azurerm_resource_group.maya_rg.name
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.maya_kv.name
}

output "app_service_name" {
  description = "Name of the App Service"
  value       = azurerm_linux_web_app.maya_api.name
}

output "app_service_default_hostname" {
  description = "Default hostname of the App Service"
  value       = azurerm_linux_web_app.maya_api.default_hostname
}

output "app_service_url" {
  description = "URL of the App Service"
  value       = "https://${azurerm_linux_web_app.maya_api.default_hostname}"
}

output "managed_identity_principal_id" {
  description = "Principal ID of the System-Assigned Managed Identity"
  value       = azurerm_linux_web_app.maya_api.identity[0].principal_id
}

output "managed_identity_tenant_id" {
  description = "Tenant ID of the System-Assigned Managed Identity"
  value       = azurerm_linux_web_app.maya_api.identity[0].tenant_id
}

output "cosmos_db_account_name" {
  description = "Name of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.maya_cosmos.name
}

output "cosmos_db_endpoint" {
  description = "Endpoint URL of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.maya_cosmos.endpoint
}

output "cosmos_db_database_name" {
  description = "Name of the Cosmos DB database"
  value       = azurerm_cosmosdb_sql_database.chatbot.name
}

output "cosmos_db_containers" {
  description = "List of Cosmos DB container names"
  value       = [for container in azurerm_cosmosdb_sql_container.containers : container.name]
}

output "cosmos_db_primary_key" {
  description = "Primary master key for Cosmos DB (sensitive)"
  value       = azurerm_cosmosdb_account.maya_cosmos.primary_key
  sensitive   = true
}

output "cosmos_db_connection_strings" {
  description = "Connection strings for Cosmos DB (sensitive)"
  value       = azurerm_cosmosdb_account.maya_cosmos.primary_sql_connection_string
  sensitive   = true
}

output "openai_account_name" {
  description = "Name of the Azure OpenAI account"
  value       = azurerm_cognitive_account.maya_openai.name
}

output "openai_endpoint" {
  description = "Endpoint URL of the Azure OpenAI account"
  value       = azurerm_cognitive_account.maya_openai.endpoint
}

output "openai_primary_key" {
  description = "Primary key for Azure OpenAI (sensitive)"
  value       = azurerm_cognitive_account.maya_openai.primary_access_key
  sensitive   = true
}

output "openai_deployments" {
  description = "List of Azure OpenAI deployment names"
  value       = [for deployment in azurerm_cognitive_deployment.openai_deployments : deployment.name]
}