from models import RequestDefinition

class ChatRequest:
    def __init__(self, user_id:str, request:RequestDefinition, session_id:str|None = None):
        self.user_id = user_id
        self.session_id = session_id
        self.request = request
