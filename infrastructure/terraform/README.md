# Step-by-Step

## Install Terraform 
```bash
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install terraform
```
## 1. Authenticate with Azure CLI 
```bash
az login
```

### 1.1 Remove any partial state (if needed)
```bash
rm -rf .terraform
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*
```

## 2. Initialize Terraform
Run the initialization command:
```bash
cd infrastructure/terraform
terraform init
```

## 3. Plan the Deployment
Review what Terraform will create:
```bash
terraform plan
```
This will show you all resources that will be created without actually creating them.

## 4. Apply the Configuration
Deploy the resources:
```bash
terraform apply
```
Type `yes` when prompted to confirm.

## 5. Verify the Deployment
After successful deployment, verify:
```bash
# Check outputs
terraform output

# Verify in Azure CLI
az webapp show --name maya-dev-api --resource-group maya-dev-rg

# Check managed identity
az webapp identity show --name maya-dev-api --resource-group maya-dev-rg
```

## 6. Enable Basic Auth Publishing (If Needed)
If Basic Auth for SCM is not enabled by default, you can set it explicitly via Azure CLI:
```bash
az resource update \
  --resource-group maya-dev-rg \
  --name scm \
  --namespace Microsoft.Web \
  --resource-type basicPublishingCredentialsPolicies \
  --parent sites/maya-dev-api \
  --set properties.allow=true
```














---

# Azure Infrastructure - Terraform Deployment

This Terraform configuration deploys the complete Azure infrastructure for the a chatbot application, including all required services with proper configuration.

## 📋 Overview

This deployment creates the following Azure resources:

### Core Services
- **App Service** (`maya-dev-api`) - Python 3.10 web application with managed identity
- **App Service Plan** - Basic B1 tier (Linux)
- **Application Insights** (`maya-dev-ais`) - Monitoring and telemetry
- **Key Vault** (`maya-dev-kv`) - Secure secrets management

### AI & Search Services
- **Azure OpenAI** (`maya-dev-openai`) - With deployments:
  - `Ada` - text-embedding-ada-002 (version 2)
  - `gpt-4o-mini` - GPT-4o-mini model (1M tokens/minute)
- **Azure AI Search** (`maya-dev-search`) - Basic tier for vector search

### Database Services
- **Cosmos DB** (`maya-dev-cosmos-db`) - Serverless NoSQL database
  - Database: `chatbot`
  - Containers: `embeddings`, `history`, `attributes`, `filters`, `requests`

## 🚀 Prerequisites

1. **Azure CLI** installed and configured
2. **Terraform** installed (>= 1.0)
3. **Azure Subscription** with appropriate permissions
4. **curl** and **jq** (for the search configuration script)

## Quick Start

```bash
# 1. Authenticate with Azure
az login

# 2. Customize configuration (optional)
nano terraform.tfvars

# 3. Initialize Terraform
terraform init

# 4. Review deployment plan
terraform plan

# 5. Deploy infrastructure
terraform apply

# 6. Configure AI Search
./configure-search.sh

# 7. View outputs
terraform output
```

## 🎯 Deployment Steps

### Step 1: Initialize Terraform

```bash
terraform init
```

### Step 2: Review the Deployment Plan

```bash
terraform plan
```

### Step 3: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. Deployment takes approximately 10-15 minutes.

### Step 4: Configure AI Search

```bash
./configure-search.sh
```

This automatically creates the data source, index, and indexer.

### Step 5: Verify Deployment

```bash
terraform output deployment_summary
```

## 🔧 Post-Deployment Manual Steps

### 1. Enable SCM Basic Auth (Required)

Azure Portal → App Service (`maya-dev-api`) → Configuration → Set **SCM Basic Auth Publishing Credentials** to `ON`

### 2. Deploy Application Code

```bash
az webapp up --name maya-dev-api --resource-group maya-dev-rg
```

## 🔐 Security & Access

### Managed Identity
The App Service has System-Assigned Managed Identity with Key Vault Secrets User role.

### Key Vault Secrets
Automatically stored:
- `COSMOS-DB-KEY`
- `OPENAI-KEY`
- `SEARCH-ADMIN-KEY`
- `APPINSIGHTS-INSTRUMENTATION-KEY`

### Access Secrets in Python

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
vault_url = os.environ["KEYVAULT_URI"]
client = SecretClient(vault_url=vault_url, credential=credential)

cosmos_key = client.get_secret("COSMOS-DB-KEY").value
```

## 📊 Monitoring

### Application Insights
```bash
terraform output -raw app_insights_connection_string
```

### App Service Logs
```bash
az webapp log tail --name maya-dev-api --resource-group maya-dev-rg
```

### Search Indexer Status
```bash
SEARCH_ENDPOINT=$(terraform output -raw search_service_endpoint)
SEARCH_KEY=$(terraform output -raw search_service_primary_key)

curl "${SEARCH_ENDPOINT}/indexers/indexer-1/status?api-version=2023-11-01" \
  -H "api-key: ${SEARCH_KEY}" | jq
```

## 🔄 Updating Infrastructure

```bash
# Modify terraform.tfvars or main.tf
terraform plan
terraform apply
```

## 🗑️ Cleanup

```bash
terraform destroy
```

⚠️ **Warning**: Permanently deletes all resources!

## 📝 Environment Variables

Automatically configured in App Service:
- `APPLICATIONINSIGHTS_CONNECTION_STRING`
- `KEYVAULT_NAME` / `KEYVAULT_URI`
- `COSMOS_DB_ENDPOINT` / `COSMOS_DB_NAME`
- `OPENAI_ENDPOINT`
- `SEARCH_ENDPOINT`

## 🐛 Troubleshooting

### Key Vault or App Service name exists
Change `key_vault_name` or `app_service_name` in `terraform.tfvars` (must be globally unique).

### Permission denied
Ensure you have Contributor/Owner role:
```bash
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

### Search indexer not running
```bash
./configure-search.sh
```

## 📚 Resources

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Azure Cosmos DB Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/)

## ✅ Deployment Checklist

- [ ] Azure CLI installed and logged in
- [ ] Terraform installed
- [ ] Customized `terraform.tfvars`
- [ ] Run `terraform init`
- [ ] Run `terraform apply`
- [ ] Run `./configure-search.sh`
- [ ] Enable SCM Basic Auth in Portal
- [ ] Deploy application code
- [ ] Verify services are running