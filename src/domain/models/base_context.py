from dataclasses import dataclass

@dataclass
class BaseContext:
    user_id: str
    session_id:str