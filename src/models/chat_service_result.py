from dataclasses import dataclass
from typing import List

from models import Source

@dataclass
class ChatServiceResult:
        user_id:str
        session_id:str
        answer:str
        sources: List[Source]