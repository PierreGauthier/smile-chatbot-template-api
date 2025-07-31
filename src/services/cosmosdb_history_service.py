import uuid
from typing import Annotated, List
from fastapi import Depends

from services import DatabaseHistoryService, CosmosDbHistoryDb, CosmosDbBase
from models import ChatMessage

class CosmosDbHistoryService(DatabaseHistoryService):
    def __init__(self, database: Annotated[CosmosDbBase, Depends(CosmosDbHistoryDb)]):
        self.database = database

    def create_message_thread(self, user_id: str, message: str) -> ChatMessage:
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
        return ChatMessage.from_dict(item_dict)
    
    def get_message_thread(self, user_id: str, session_id: str) -> List[ChatMessage]:
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
        return [ChatMessage.from_dict(doc) for doc in items]
    
    def upsert_message(self, message:ChatMessage):
        if not message.id:
            message.id = str(uuid.uuid4())
        container = self.database.get_container()
        request_thread_body = ChatMessage.to_dict(message)
        container.upsert_item(body=request_thread_body)
        return message
 
        
    
    
