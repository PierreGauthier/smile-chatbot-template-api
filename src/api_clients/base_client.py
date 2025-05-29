import uuid
from base64 import b64encode

CORRELATION_ID_HEADER_KEY = "X-CorrelationId"
AUTHORIZATION_HEADER_KEY = "Authorization"
AUTHORIZATION_BASIC_TOKEN_PREFIX = "Basic"
CONTENT_TYPE_KEY = "Content-Type"
CONTENT_TYPE_JSON_VALUE = "application/json"

class BaseClient():
    def __init__(self, base_url: str):
        self.api_base_url = base_url

    def create_x_correlation_id(self):
        key = CORRELATION_ID_HEADER_KEY
        value = str(uuid.uuid4())
        return (key, value)
    
    def create_basic_auth(self, username, password):
        return (AUTHORIZATION_HEADER_KEY, self._encode_basic_auth(username, password))
    
    def create_json_content_type(self):
        return (CONTENT_TYPE_KEY, CONTENT_TYPE_JSON_VALUE)
    
    def _encode_basic_auth(self, username, password):
        token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
        return f'{AUTHORIZATION_BASIC_TOKEN_PREFIX} {token}'