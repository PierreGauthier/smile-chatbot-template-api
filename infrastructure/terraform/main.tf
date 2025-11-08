terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "maya_rg" {
  name     = var.resource_group_name
  location = var.location
  tags = var.tags
}

# Generate a random suffix for Key Vault name
resource "random_string" "kv_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_key_vault" "maya_kv" {
  name                       = "${var.key_vault_name}-${random_string.kv_suffix.result}"
  location                   = azurerm_resource_group.maya_rg.location
  resource_group_name        = azurerm_resource_group.maya_rg.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  # Enable RBAC authorization (recommended over access policies)
  enable_rbac_authorization = true

  # Network access (allow access from all networks for dev)
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"
  }
  tags = var.tags
  depends_on = [azurerm_resource_group.maya_rg]
}

# Application Insights
resource "azurerm_application_insights" "maya" {
  name                = var.app_insights_name
  location            = azurerm_resource_group.maya_rg.location
  resource_group_name = azurerm_resource_group.maya_rg.name
  application_type    = "web"
  tags = var.tags
  depends_on = [azurerm_key_vault.maya_kv]
}

# Grant Key Vault Administrator role to current user (you)
# This allows you to manage secrets via Azure Portal or CLI
resource "azurerm_role_assignment" "kv_admin" {
  scope                = azurerm_key_vault.maya_kv.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
  depends_on = [azurerm_key_vault.maya_kv]
}

resource "azurerm_service_plan" "maya_plan" {
  name                = "${var.app_service_name}-plan"
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = "B1"
  tags = var.tags
  depends_on = [azurerm_resource_group.maya_rg]
}

resource "azurerm_linux_web_app" "maya_api" {
  name                = var.app_service_name
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = azurerm_service_plan.maya_plan.id

  # Enable System-Assigned Managed Identity
  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = var.python_version
    }

    # Startup command for FastAPI with uvicorn
    app_command_line = "PYTHONPATH= uvicorn app:app --host 0.0.0.0 --port $PORT --app-dir src --log-level info"

    cors {
      allowed_origins = ["*"]  # Adjust for production
    }
  }

  # Enable SCM Basic Auth Publishing Credentials
  # Note: This is enabled by default, but explicitly setting for clarity
  app_settings = merge(
    {
      "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
      # Add Key Vault URL as app setting for easy reference
      "KEY_VAULT_URL"                  = azurerm_key_vault.maya_kv.vault_uri
    },
    var.app_settings
  )

  # Explicitly enable basic auth for SCM (enabled by default in Azure)
  # This is controlled at the app service level
  https_only = true
  tags = var.tags
  depends_on = [azurerm_service_plan.maya_plan]
}

# Grant App Service access to Key Vault secrets
# This allows the App Service managed identity to read secrets
resource "azurerm_role_assignment" "app_kv_secrets" {
  scope                = azurerm_key_vault.maya_kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_web_app.maya_api.identity[0].principal_id

  depends_on = [
    azurerm_key_vault.maya_kv,
    azurerm_linux_web_app.maya_api
  ]
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "maya_cosmos" {
  name                = var.cosmos_db_account_name
  location            = azurerm_resource_group.maya_rg.location
  resource_group_name = azurerm_resource_group.maya_rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  # Serverless capacity mode
  capabilities {
    name = "EnableServerless"
  }

  # Consistency policy
  consistency_policy {
    consistency_level = "Session"
  }

  # Single region deployment for dev
  geo_location {
    location          = azurerm_resource_group.maya_rg.location
    failover_priority = 0
  }

  # Enable automatic failover (optional for serverless)
  automatic_failover_enabled = false
  tags = var.tags
  depends_on = [azurerm_resource_group.maya_rg]
}

# Create Cosmos DB SQL Database
resource "azurerm_cosmosdb_sql_database" "chatbot" {
  name                = var.cosmos_db_database_name
  resource_group_name = azurerm_resource_group.maya_rg.name
  account_name        = azurerm_cosmosdb_account.maya_cosmos.name

  depends_on = [azurerm_cosmosdb_account.maya_cosmos]
}

# Create Cosmos DB SQL Containers
resource "azurerm_cosmosdb_sql_container" "containers" {
  for_each = { for container in var.cosmos_db_containers : container.name => container }

  name                = each.value.name
  resource_group_name = azurerm_resource_group.maya_rg.name
  account_name        = azurerm_cosmosdb_account.maya_cosmos.name
  database_name       = azurerm_cosmosdb_sql_database.chatbot.name
  partition_key_paths = [each.value.partition_key]

  # Serverless doesn't support throughput settings
  # No autoscale_settings or throughput needed

  depends_on = [azurerm_cosmosdb_sql_database.chatbot]
}

# Grant App Service access to Cosmos DB (Data Contributor role)
resource "azurerm_role_assignment" "app_cosmos_contributor" {
  scope                = azurerm_cosmosdb_account.maya_cosmos.id
  role_definition_name = "Cosmos DB Account Reader Role"
  principal_id         = azurerm_linux_web_app.maya_api.identity[0].principal_id

  depends_on = [
    azurerm_cosmosdb_account.maya_cosmos,
    azurerm_linux_web_app.maya_api
  ]
}

# Grant App Service data plane access to Cosmos DB
# This allows the managed identity to read/write data
resource "azurerm_cosmosdb_sql_role_assignment" "app_cosmos_data" {
  resource_group_name = azurerm_resource_group.maya_rg.name
  account_name        = azurerm_cosmosdb_account.maya_cosmos.name
  role_definition_id  = "${azurerm_cosmosdb_account.maya_cosmos.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  principal_id        = azurerm_linux_web_app.maya_api.identity[0].principal_id
  scope               = azurerm_cosmosdb_account.maya_cosmos.id

  depends_on = [
    azurerm_cosmosdb_account.maya_cosmos,
    azurerm_linux_web_app.maya_api
  ]
}

# Create Azure OpenAI Account
resource "azurerm_cognitive_account" "maya_openai" {
  name                  = var.openai_account_name
  location              = azurerm_resource_group.maya_rg.location
  resource_group_name   = azurerm_resource_group.maya_rg.name
  kind                  = "OpenAI"
  sku_name              = var.openai_sku
  custom_subdomain_name = var.openai_account_name

  # Allow access from all networks for development
  network_acls {
    default_action = "Allow"
  }
  tags = var.tags
  depends_on = [azurerm_resource_group.maya_rg]
}

# Create Azure OpenAI Model Deployments
resource "azurerm_cognitive_deployment" "openai_deployments" {
  for_each = { for deployment in var.openai_deployments : deployment.name => deployment }

  name                 = each.value.name
  cognitive_account_id = azurerm_cognitive_account.maya_openai.id
  model {
    format  = "OpenAI"
    name    = each.value.model_name
    version = each.value.model_version
  }
  scale {
    type     = each.value.scale_type     # e.g., "Standard" or "Manual"
    capacity = each.value.capacity       # e.g., 1, 2, ...
  }

  depends_on = [azurerm_cognitive_account.maya_openai]
}

# Azure AI Search Service
resource "azurerm_search_service" "maya_search" {
  name                = var.search_service_name
  resource_group_name = azurerm_resource_group.maya_rg.name
  location            = azurerm_resource_group.maya_rg.location
  sku                 = var.search_sku
  replica_count       = var.search_replica_count
  partition_count     = var.search_partition_count

  # Enable System-Assigned Managed Identity for the Search Service
  identity {
    type = "SystemAssigned"
  }

  tags       = var.tags
  depends_on = [azurerm_resource_group.maya_rg]
}

# Grant Search Service access to Cosmos DB (Reader role for metadata)
resource "azurerm_role_assignment" "search_cosmos_reader" {
  scope                = azurerm_cosmosdb_account.maya_cosmos.id
  role_definition_name = "Cosmos DB Account Reader Role"
  principal_id         = azurerm_search_service.maya_search.identity[0].principal_id

  depends_on = [
    azurerm_cosmosdb_account.maya_cosmos,
    azurerm_search_service.maya_search
  ]
}

# Grant Search Service data plane access to Cosmos DB
resource "azurerm_cosmosdb_sql_role_assignment" "search_cosmos_data" {
  resource_group_name = azurerm_resource_group.maya_rg.name
  account_name        = azurerm_cosmosdb_account.maya_cosmos.name
  role_definition_id  = "${azurerm_cosmosdb_account.maya_cosmos.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000001"
  principal_id        = azurerm_search_service.maya_search.identity[0].principal_id
  scope               = azurerm_cosmosdb_account.maya_cosmos.id

  depends_on = [
    azurerm_cosmosdb_account.maya_cosmos,
    azurerm_search_service.maya_search
  ]
}
