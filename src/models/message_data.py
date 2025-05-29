class MessageData:
    def __init__(self, content:str):
        self.content = content
    
    def to_dict(self):
        return { "content": self.content }
    
    @staticmethod
    def from_dict(data: dict):
        return MessageData(
            content=data.get("content", "")
        )