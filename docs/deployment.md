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
- SCM Basic Auth Publishing Credentials: On
- Startup Command (Settings > Configuration > Stack settings > Startup command): 
  ```BASH
  PYTHONPATH= uvicorn app:app --host 0.0.0.0 --port $PORT --app-dir src --log-level info
  ```
- Managed Identity: Activated (Settings > Identity > System assigned > Status = On)
- Run the script `data/helper.ipynb` to obtain the environment variables for the App Service. Paste it on (Settings > Environment variables > App Settings > Advanced edit). Make sure to enter the name of your key vault service (see below) in the script (KEYVAULT_NAME).

### Create an App Key Vault
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
   - Copy the **publish profile** content between
        ```html
        <publishData>...</publishData>
        ```

2. **Add GitHub Secrets:**
   - In **GitHub Repo → Settings → Secrets and variables → Actions → New Repository Secret**
   - Add a secret named **AZURE_WEBAPP_PUBLISH_PROFILE**
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
             publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
             package: "."
   ```

4. **Commit & Push Changes to GitHub**
   ```bash
   git add .
   git commit -m "Added GitHub Actions deployment"
   git push
   ```

5. **GitHub Actions will deploy your FastAPI app** automatically.

