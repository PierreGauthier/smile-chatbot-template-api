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

# Generate a random suffix for Key Vault name
resource "random_string" "kv_suffix" {
  length  = 6
  special = false
  upper   = false
}

data "azurerm_client_config" "current" {}

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

  tags = {
    Environment = "Development"
    Project     = "MAYA"
    ManagedBy   = "Terraform"
  }

  depends_on = [azurerm_resource_group.maya_rg]
}

resource "azurerm_resource_group" "maya_rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Development"
    Project     = "MAYA"
    ManagedBy   = "Terraform"
  }
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