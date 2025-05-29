import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def load_keyvault_env(key_vault_name: str):
    if key_vault_name:
        key_vault_name_uri = f"https://{key_vault_name}.vault.azure.net"
        credential = DefaultAzureCredential()
        key_vault_client = SecretClient(vault_url=key_vault_name_uri, credential=credential)

        secret_properties = key_vault_client.list_properties_of_secrets()
        for secret_property in secret_properties:
            secret = key_vault_client.get_secret(secret_property.name)
            os.environ[secret_property.name.replace("--", "_")] = secret.value
