import uuid
from typing import Annotated
from fastapi import Depends
from typing import List

from services import IDatabaseHistoryService
from memory import CosmosDbHistoryDb
from models import ChatThread, ChatMessage
from mappers import ChatThreadMapper

class CosmosDbHistoryService(IDatabaseHistoryService):
    def __init__(self, database: Annotated[CosmosDbHistoryDb, Depends(CosmosDbHistoryDb)]):
        self.database = database

    def get_chat_thread(self, user_id: str, session_id: str) -> ChatThread:
        container = self.database.get_container()
        thread = container.read_item(item=session_id, partition_key=user_id)            
        return ChatThreadMapper.from_dict(thread)
    
    def get_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        thread:ChatThread = self.get_chat_thread(user_id=user_id, session_id=session_id)
        messages:List[ChatMessage] = thread.messages
        return messages
    
    def insert_message(self, user_id: str, session_id: str, new_message:ChatMessage) -> ChatMessage:
        container = self.database.get_container()
        thread:ChatThread = self.get_chat_thread(user_id=user_id, session_id=session_id)
        messages:List[ChatMessage] = thread.messages
        messages.append(new_message)
        thread_body = ChatThreadMapper.to_dict(thread)
        container.upsert_item(body=thread_body)

    def insert_human_message(self, user_id: str, session_id: str, message:str) -> ChatMessage:
        self.insert_message(user_id=user_id, session_id=session_id, new_message=ChatMessage.create_human_message(message))
    
    def insert_ai_message(self, user_id: str, session_id: str, message:str) -> ChatMessage:
        self.insert_message(user_id=user_id, session_id=session_id, new_message=ChatMessage.create_ai_message(message))
    
    def create_chat_thread(self, user_id: str) -> ChatThread:
        container = self.database.get_container()
        session_id = str(uuid.uuid4())
        item_dict = container.upsert_item(
            body={
                "id": session_id,
                "user_id": user_id,
                "messages": []
            }
        )
        return ChatThreadMapper.from_dict(item_dict)

    