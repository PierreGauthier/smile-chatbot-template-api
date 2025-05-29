from config import Settings
from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey

class CosmosDbBase():
    def __init__(self, container: str, particion_key:str, settings: Settings):
        self.cosmos_endpoint = settings.azure_cosmos_url
        self.cosmos_database = settings.azure_cosmos_database
        self.credential = settings.azure_cosmos_key
        self.cosmos_container = container
        self.partition_key  = particion_key
        self.client = CosmosClient(url=self.cosmos_endpoint, credential=self.credential)
        
    def get_container(self) -> ContainerProxy:
        database = self.client.create_database_if_not_exists(self.cosmos_database)
        container = database.create_container_if_not_exists(
            self.cosmos_container,
            partition_key=PartitionKey(f"/{self.partition_key}"))
        return container