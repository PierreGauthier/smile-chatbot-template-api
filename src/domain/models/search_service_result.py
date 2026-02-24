from dataclasses import dataclass
from typing import List

from domain.models import SearchResponseItem

@dataclass
class SearchServiceResult:
    user_id: str
    session_id: str
    answer: str
    products: List[SearchResponseItem]
    is_final: bool = True
    url: str = None