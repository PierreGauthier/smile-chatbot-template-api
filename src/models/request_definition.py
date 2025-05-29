from models import RequestDefinitionField

class RequestDefinition:
    """To use if needed.
    Add fields if extra information is required from the user.
    Example: The subject of the conversation
    """
    def __init__(self, subject:str = ""):
        self.subject = subject

    def merge(self, new_request:RequestDefinitionField):
        self.subject = new_request.subject if new_request.subject else self.subject

    def is_complete(self):
        return self.subject
    
    def _print(self):
        print(f"Subject: {self.subject}")
    