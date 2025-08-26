class ApiResponse:

    def __init__(self, code:int, message:str, query:str = ""):
        self.code = code
        self.message = message
        self.query = query