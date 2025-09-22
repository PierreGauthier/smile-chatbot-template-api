import uuid
from typing import Annotated, List, Type
from fastapi import Depends

from domain.services.database import DatabaseHistoryService, T

from infrastructure.azure.services import CosmosDb

from config import Settings, get_settings

class CosmosDbHistoryService(DatabaseHistoryService[T]):
    def __init__(self, message_class: Type[T], settings: Annotated[Settings, Depends(get_settings)]):
        super().__init__(message_class)
        self.database = CosmosDb(
            container=settings.azure_cosmos_history_container,
            partition_key=settings.azure_cosmos_history_partition_key,
            settings=settings
        )

    def create_message_thread(self, user_id: str, message: str) -> T:
        container = self.database.get_container()
        session_id = str(uuid.uuid4())
        id = str(uuid.uuid4())
        item_dict = container.upsert_item(
            body={
                "id": id,
                "session_id": session_id,
                "user_id": user_id,
                "type": "human",
                "data": { "content": message }
            }
        )
        return self.message_class.from_dict(item_dict)
    
    def get_message_thread(self, user_id: str, session_id: str) -> List[T]:
        """
        Fetch every chat message that belongs to a (user_id, session_id) pair and return them as domain objects in chronological order.
        """
        container = self.database.get_container()
        query = """
            SELECT *
            FROM   c
            WHERE  c.session_id = @session_id
            AND    c.user_id = @user_id
        """
        parameters = [
            {"name": "@session_id", "value": session_id},
            {"name": "@user_id",    "value": user_id},
        ]
        items = list(
            container.query_items(
                query         = query,
                parameters    = parameters,
                partition_key = user_id,
                enable_cross_partition_query = False
            )
        )
        return [self.message_class.from_dict(doc) for doc in items]
    
    def upsert_message(self, message:T):
        if not message.id:
            message.id = str(uuid.uuid4())
        container = self.database.get_container()
        request_thread_body = message.to_dict()
        container.upsert_item(body=request_thread_body)
        return message
 