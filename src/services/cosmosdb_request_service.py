import uuid
from typing import Annotated
from fastapi import Depends

from services import IDatabaseRequestService
from memory import CosmosDbRequestDb
from models import ChatRequest
from mappers import ChatRequestMapper

class CosmosDbRequestService(IDatabaseRequestService):
    def __init__(self, database: Annotated[CosmosDbRequestDb, Depends(CosmosDbRequestDb)]):
        self.database = database

    def get_request(self, user_id: str, session_id: str) -> ChatRequest:
        container = self.database.get_container()
        request = container.read_item(item=session_id, partition_key=user_id)            
        return ChatRequestMapper.from_dict(request)
    
    def create_request(self, user_id: str) -> ChatRequest:
        container = self.database.get_container()
        session_id = str(uuid.uuid4())
        item_dict = container.upsert_item(
            body={
                "id": session_id,
                "user_id": user_id,
                "request": {}
            }
        )
        return ChatRequestMapper.from_dict(item_dict)

    def update_request(self, new_request: ChatRequest)-> ChatRequest:
        container = self.database.get_container()
        request:ChatRequest = self.get_request(user_id=new_request.user_id, session_id=new_request.session_id)
        request.request = new_request.request
        thread_body = ChatRequestMapper.to_dict(request)
        container.upsert_item(body=thread_body)
