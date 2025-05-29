from dataclasses import dataclass

@dataclass
class MessageData:
    content:str
    
    def to_dict(self):
        return { "content": self.content }
    
    @staticmethod
    def from_dict(data: dict):
        return MessageData(
            content=data.get("content", "")
        )