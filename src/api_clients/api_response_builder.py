class ApiResponseBuilder:

    def __init__(self, message_404:str):
        self.messages = {
            200: "",
            400: "We are having communicating with the external application.",
            403: "We are having access problems.",
            500: "Internal server error."
        }
        self.messages[404] = message_404