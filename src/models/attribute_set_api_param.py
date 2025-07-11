from models import ApiParam

class AttributeSetApiParam(ApiParam):

    def __init__(self, page:int, page_size:int, query:str = ""):
        super().__init__(query=query)
        self.page = page
        self.page_size = page_size