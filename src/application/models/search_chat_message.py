from dataclasses import dataclass
from typing import List

from domain.models import ChatMessage, SearchResponseItem
from application.models import SearchMessageData

@dataclass
class SearchChatMessage(ChatMessage):

    @classmethod
    def build_human_message(
            cls, 
            session_id:str, 
            user_id:str, 
            content:str, 
            id:str=None):
        return SearchChatMessage(
            id=id, 
            session_id=session_id, 
            user_id=user_id, 
            type="human", 
            data=SearchMessageData(content=content, products=[])
        )
    
    @classmethod
    def build_ai_message(
            cls, 
            session_id:str, 
            user_id:str, 
            content:str, 
            id:str=None,
            products:List[SearchResponseItem] = []):
        return SearchChatMessage(
            id=id, 
            session_id=session_id, 
            user_id=user_id, 
            type="ai", 
            data=SearchMessageData(content=content, products=products)
        )
