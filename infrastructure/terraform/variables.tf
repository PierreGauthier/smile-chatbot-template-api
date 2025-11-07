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