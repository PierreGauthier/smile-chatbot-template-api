import uuid
from typing import Annotated, List
from fastapi import Depends
from google.cloud import firestore

from domain.services.database import DatabaseHistoryService
from domain.models import ChatMessage

from infrastructure.gcp.services import Firestore

from config import Settings, get_settings

class FirestoreHistoryService(DatabaseHistoryService):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.database = Firestore(
            collection=settings.firestore_history_collection,
            settings=settings
        )

    def create_message_thread(self, user_id: str, message: str) -> ChatMessage:
        collection_ref = self.database.get_collection()
        session_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        doc_data = {
            "id": message_id,
            "session_id": session_id,
            "user_id": user_id,
            "type": "human",
            "data": {"content": message},
            "timestamp": firestore.SERVER_TIMESTAMP  # Optional: add timestamp for ordering
        }
        
        # Create document with the message ID as document ID
        doc_ref = collection_ref.document(message_id)
        doc_ref.set(doc_data)
        
        # Return the created message
        return ChatMessage.from_dict(doc_data)
    
    def get_message_thread(self, user_id: str, session_id: str) -> List[ChatMessage]:
        """
        Fetch every chat message that belongs to a (user_id, session_id) pair 
        and return them as domain objects in chronological order.
        """
        collection_ref = self.database.get_collection()
        
        # Create compound query for user_id and session_id
        query = (collection_ref
                .where("user_id", "==", user_id)
                .where("session_id", "==", session_id)
                .order_by("timestamp"))  # Order by timestamp if available, otherwise by document creation
        
        # Execute query
        docs = query.stream()
        
        # Convert to ChatMessage objects
        messages = []
        for doc in docs:
            doc_data = doc.to_dict()
            messages.append(ChatMessage.from_dict(doc_data))
        
        return messages
    
    def upsert_message(self, message: ChatMessage) -> ChatMessage:
        if not message.id:
            message.id = str(uuid.uuid4())
        
        collection_ref = self.database.get_collection()
        
        # Convert message to dictionary
        message_dict = ChatMessage.to_dict(message)
        
        # Add timestamp if not present (useful for ordering)
        if "timestamp" not in message_dict:
            message_dict["timestamp"] = firestore.SERVER_TIMESTAMP
        
        # Use message ID as document ID
        doc_ref = collection_ref.document(message.id)
        doc_ref.set(message_dict, merge=True)  # merge=True for upsert behavior
        
        return message

