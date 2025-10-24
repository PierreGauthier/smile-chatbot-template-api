For simplicity in the notation, we assume that we deploy the application for a costumer called **Maya** (development environment).

## **Step 1: Prerequisites**
Ensure you have the following:
1. **Azure Account** 
2. **Azure CLI** installed - [Download here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
3. **GitHub Repository** - Your FastAPI app should be in a GitHub repo.
4. **Python 3.10** installed locally.
5. An **App Service** called `maya-dev-api` in a resource group called `maya-dev-rg`

### Create an App Service on Azure
- Name: **maya-dev-api**
- Runtime Stack: Python - 3.10
- App Service Plan: Basic (B1)
- SCM Basic Auth Publishing Credentials: On (Settings > Configuration > SCM Basic Auth Publishing Credentials)
- Startup Command (Settings > Configuration > Stack settings > Startup command): 
  ```BASH
  PYTHONPATH= uvicorn app:app --host 0.0.0.0 --port $PORT --app-dir src --log-level info
  ```
- Managed Identity: Activated (Settings > Identity > System assigned > Status = On)
- Run the script `data/helper.ipynb` to obtain the environment variables for the App Service. Paste it on (Settings > Environment variables > App Settings > Advanced edit). Make sure to enter the name of your key vault service (see below) in the script (KEYVAULT_NAME).

### Create an AppInsights service on Azure
- Name: maya-dev-ais
- Get the connection string (Overview > Connection string)

### Create a Cosmos DB service on Azure
- Name: **maya-dev-cosmos-db**
- Type: Cosmos DB for No SQL
- Capacity mode: Serverless
- Databases:
	- Name: `chatbot`
		- Container: `embeddings` - Partition Key: `/doc_type`
    - Container: `history` - Partition key: `/user_id`
    - Container: `attributes` - Partition key: `/project_id`
    - Container: `filters` - Partition key: `attribute_id`
		- Container: `requests` - Partition Key: `/user_id`
- Get the endpoint and access key (Settings > Keys)

## Create an OpenAI service on Azure
- Name: **maya-dev-openai**
- Pricing tier: Standard
- Add Deployments (Overview > Go to Azure Ai Foundry portal -> Shared resources > Deployments):
	- Embedding Model Name: Ada, Model: text-embedding-ada-002, Version: 2
	- Completion Model Name: gpt-4o-mini, Model: gpt-4o-mini (for staging, set 1M tokens per minute)
- Get key and endpoint (Resource Management > Keys and Endpoint)

### Create an App Key Vault on Azure
- Name: **maya-dev-kv**
- Role Assignments:
	- Key Vault Administrator: (you)
	- Key Vault Secrets User: App Service (`maya-dev-api`)
- Run the script `data/helper.ipynb` to obtain the secrets for the Key Vault.

---

## **Step 2: Configure Deployment from GitHub using GitHub Actions**

1. **Get the Azure Publish Profile:**
    ```bash
    az webapp deployment list-publishing-profiles --name maya-dev-api --resource-group maya-dev-rg --xml
    ```
    or... go to the Azure Portal (Overview > Download publish profile)
    - Copy the **publish profile** content between
    ```html
    <publishData>...</publishData>
    ```

2. **Add GitHub Secrets:**
   - In **GitHub Repo → Settings → Secrets and variables → Actions → New Repository Secret**
   - Add a secret named **AZURE_WEBAPP_PUBLISH_DEVELOP_PROFILE**
   - Paste the **publish profile** content.

3. **Create GitHub Actions Workflow:**
   In your GitHub repo, create `.github/workflows/deploy.yml` and add the following:

    ```yaml
    name: Deploy FastAPI to Azure

    on:
        push:
            branches:
                - main  # Change to your deployment branch

    jobs:
        build-and-deploy:
            runs-on: ubuntu-latest
            steps:
            - name: Checkout Code
                uses: actions/checkout@v3

            - name: Setup Python
                uses: actions/setup-python@v4
                with:
                    python-version: '3.10'

            - name: Install Dependencies
                run: |
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt

            - name: Deploy to Azure
                uses: azure/webapps-deploy@v2
                with:
                    app-name: "maya-dev-api"
                    publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_DEVELOP_PROFILE }}
                    package: "."
    ```

4. **Commit & Push Changes to GitHub**
    ```bash
    git add .
    git commit -m "Added GitHub Actions deployment"
    git push
    ```

5. **GitHub Actions will deploy your FastAPI app** automatically.

