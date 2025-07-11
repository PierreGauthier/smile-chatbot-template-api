from typing import Annotated
from fastapi import Depends
from config import Settings, get_settings

from services import CosmosDbBase

class CosmosDbHistoryDb(CosmosDbBase):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        super().__init__(
            settings=settings, 
            container=settings.azure_cosmos_history_container, 
            partition_key=settings.azure_cosmos_history_partition_key
        )
