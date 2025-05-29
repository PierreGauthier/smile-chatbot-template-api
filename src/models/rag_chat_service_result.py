from dataclasses import dataclass
from typing import List

from models import DocumentSource

@dataclass
class RagChatServiceResult:
        user_id:str
        session_id:str
        answer:str
        sources: List[DocumentSource]