from dataclasses import dataclass, field
from typing import List

from domain.models import ChatMessage, Language
@dataclass
class BaseContext:
    user_id: str
    session_id:str
    is_first_call:bool
    input_message: str
    chat_lang:Language = None
    message_thread: List[ChatMessage] = field(default_factory=list)
    exchange: str = ""
    ai_answer:str = ""