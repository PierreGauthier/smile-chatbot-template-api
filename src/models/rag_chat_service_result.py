class RagChatServiceResult:
    def __init__(self, user_id:str, session_id:str, answer:str, complete:bool):
        self.user_id = user_id
        self.session_id = session_id
        self.answer = answer
        self.complete = complete 