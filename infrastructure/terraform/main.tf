terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
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
  app_settings = {
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
  }

  # Explicitly enable basic auth for SCM (enabled by default in Azure)
  # This is controlled at the app service level
  https_only = true

  depends_on = [azurerm_service_plan.maya_plan]
}

