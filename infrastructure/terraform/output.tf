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