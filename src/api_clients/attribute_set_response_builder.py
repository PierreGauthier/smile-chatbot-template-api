from requests import Response

from api_clients import ApiResponseBuilder
from models import ElasticSuiteApiResponse, AttributeSetApiResponse, AttributeSetApiParam

class AttributeSetResponseBuilder(ApiResponseBuilder):

    def __init__(self):
        super().__init__("We can't find information about the attribute set.")

    def build_response(self, params: AttributeSetApiParam, response: Response) -> ElasticSuiteApiResponse:
        if response.status_code == 200:
            return AttributeSetApiResponse.build_from_api_response(response.json(), params)
        else:
            error_message = self.messages.get(response.status_code, "Unknown error.")
            return ElasticSuiteApiResponse(response.status_code, message=error_message)
