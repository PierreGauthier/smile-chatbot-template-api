from api_clients import BaseClient
from typing import Annotated
from fastapi import Depends

from config import Settings, get_settings
from api_clients import AttributeSetResponseBuilder
from models import AttributeSetApiParam, AttributeSetApiResponse

class ElasticSuiteAttributeSetClient(BaseClient):
    def __init__(
            self, 
            settings: Annotated[Settings, Depends(get_settings)],
            attribute_set_response_builder: Annotated[AttributeSetResponseBuilder, Depends(AttributeSetResponseBuilder)]):
        super().__init__(settings.elastic_suite_api_base_url)
        self.settings = settings
        self.attribute_set_response_builder = attribute_set_response_builder

    def get_attribute_set(self, params: AttributeSetApiParam) -> AttributeSetApiResponse:
        url = f"{self.api_base_url}/{self.settings.elastic_suite_attribute_set_endpoint}?page={params.page}&pageSize={params.page_size}"
        query = f"GET /{self.settings.elastic_suite_attribute_set_endpoint}?page={params.page}&pageSize={params.page_size}"
        # print(url)
        response = self.get(
            url=url, 
            username=self.settings.elastic_suite_username, 
            pwd=self.settings.elastic_suite_password
        )
        params.query = query
        return self.attribute_set_response_builder.build_response(params, response)