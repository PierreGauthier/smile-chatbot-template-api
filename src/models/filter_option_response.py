class FilterOptionResponse:

    def __init__(self, key:str, value:str):
        self.key = key
        self.value = value

    def build_from_api_response(response:dict):
        return FilterOptionResponse(
            key=response.get("key", None),
            value=response.get("value", None)
        )