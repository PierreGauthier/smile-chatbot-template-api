class ApiResponseBuilder:
    """Builds a reusable map of HTTP status codes to user-facing messages.

    Populates default messages for common error codes while allowing the caller
    to override the `404` message at instantiation time.
    """
    def __init__(self, message_404:str):
        self.messages = {
            200: "",
            400: "We are having communicating with the external application.",
            404: "Application not found",
            403: "We are having access problems.",
            500: "Internal server error."
        }
        self.messages[404] = message_404
