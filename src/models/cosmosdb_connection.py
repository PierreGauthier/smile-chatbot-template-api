from dataclasses import dataclass

@dataclass
class CosmosDbConnection:
    endpoint:str
    key:str
    database:str
    container:str
    partition_key:str