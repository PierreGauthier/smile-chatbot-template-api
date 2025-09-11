from typing import List

from domain.models import SearchResponseItem, ApiResponse

class SearchApiResponse(ApiResponse):
    def __init__(
            self, 
            total_count:int,
            items:List[SearchResponseItem], 
            code:int, 
            message:str = "", 
            query:str = ""):
        super().__init__(code=code, message=message, query=query)
        self.total_count = total_count
        self.items = items
