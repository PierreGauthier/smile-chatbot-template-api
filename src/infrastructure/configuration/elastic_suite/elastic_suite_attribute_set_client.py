from api_clients import BaseClient
from typing import Annotated
from fastapi import Depends

from config import Settings, get_settings
from infrastructure.configuration.elastic_suite import ElasticSuiteAttributeSetResponseBuilder
from models import AttributeSetApiParam, AttributeSetApiResponse

class ElasticSuiteAttributeSetClient(BaseClient):
    def __init__(
            self, 
            settings: Annotated[Settings, Depends(get_settings)],
            attribute_set_response_builder: Annotated[ElasticSuiteAttributeSetResponseBuilder, Depends(ElasticSuiteAttributeSetResponseBuilder)]):
        super().__init__(settings.elastic_suite_api_base_url)
        self.settings = settings
        self.attribute_set_response_builder = attribute_set_response_builder

    def get_attribute_set(self, params: AttributeSetApiParam) -> AttributeSetApiResponse:
        url = f"{self.api_base_url}/{self.settings.elastic_suite_attribute_set_endpoint}?page={params.page}&pageSize={params.page_size}"
        query = f"GET /{self.settings.elastic_suite_attribute_set_endpoint}?page={params.page}&pageSize={params.page_size}"
        (x_correlation_id_key, x_correlation_id_value) = self.create_x_correlation_id()
        (content_type_key, content_type_value) = self.create_json_content_type()
        (basic_auth_key, basic_auth_value) = self.create_basic_auth(
            username=self.settings.elastic_suite_username, 
            password=self.settings.elastic_suite_password
        )
        headers = {
            x_correlation_id_key: x_correlation_id_value,
            content_type_key: content_type_value,
            basic_auth_key: basic_auth_value
        }
        # print(url)
        response = self.get(url=url, headers=headers)
        params.query = query
        return self.attribute_set_response_builder.build_response(params, response)

    