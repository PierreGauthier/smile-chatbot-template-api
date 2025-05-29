from typing import List

from models import ChatMessage

class ChatThread:
    def __init__(self, user_id:str, messages: List[ChatMessage] = [], session_id:str|None = None):
        self.user_id = user_id
        self.session_id = session_id
        self.messages = messages