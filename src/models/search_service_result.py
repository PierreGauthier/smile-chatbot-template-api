from dataclasses import dataclass
from typing import List

from models import SearchResponseItem

@dataclass
class SearchServiceResult:
        user_id:str
        session_id:str
        answer:str
        products: List[SearchResponseItem]