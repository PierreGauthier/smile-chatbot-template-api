from dataclasses import dataclass
from typing import List

from domain.models import ChatMessage, Source
from application.models import RagMessageData

@dataclass
class RagChatMessage(ChatMessage):

    @classmethod
    def build_human_message(
            cls, 
            session_id:str, 
            user_id:str, 
            content:str, 
            id:str=None):
        return RagChatMessage(
            id=id, 
            session_id=session_id, 
            user_id=user_id, 
            type="human", 
            data=RagMessageData(content=content, sources=[])
        )
    
    @classmethod
    def build_ai_message(
            cls, 
            session_id:str, 
            user_id:str, 
            content:str, 
            id:str=None,
            sources:List[Source] = []):
        return RagChatMessage(
            id=id, 
            session_id=session_id, 
            user_id=user_id, 
            type="ai", 
            data=RagMessageData(content=content, sources=sources)
        )
