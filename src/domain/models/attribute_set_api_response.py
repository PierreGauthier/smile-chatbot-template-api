from typing import List
from domain.models import ApiResponse, AttributeSetDto

class AttributeSetApiResponse(ApiResponse):
    def __init__(
            self, 
            attributes:List[AttributeSetDto], 
            code:int, 
            message:str = "", 
            query:str = ""):
        super().__init__(code=code, message=message, query=query)
        self.attributes = attributes