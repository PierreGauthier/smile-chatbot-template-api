
class RagChatbotMessage:
    def __init__(self, is_ai_message:bool, message:str):
        self.is_ai_message = is_ai_message
        self.message = message

    @staticmethod
    def create_human_message(message):
        return RagChatbotMessage(is_ai_message=False, message=message)
    
    @staticmethod
    def create_ai_message(message):
        return RagChatbotMessage(is_ai_message=True, message=message)

    