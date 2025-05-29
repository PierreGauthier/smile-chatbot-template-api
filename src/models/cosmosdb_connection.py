class CosmosDbConnection:
    def __init__(self, endpoint:str, key:str, database:str, container:str, partition_key:str):
        self.endpoint = endpoint
        self.key = key
        self.database = database
        self.container = container
        self.partition_key = partition_key