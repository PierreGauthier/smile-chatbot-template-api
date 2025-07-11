class ElasticSuiteApiResponse:

    def __init__(self, code:int, message:str, formatted_message:str = None, query:str = ""):
        self.code = code
        self.message = message
        self.formatted_message = formatted_message if formatted_message else message
        self.query = query