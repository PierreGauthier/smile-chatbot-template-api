from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from models import (
    AttributeSetApiParam, 
    AttributeSetApiResponse,
    SetupServiceResult
)
from api_clients import ElasticSuiteAttributeSetClient

class ConversationalSearchSetupService:

    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            api_client:Annotated[ElasticSuiteAttributeSetClient, Depends(ElasticSuiteAttributeSetClient)]):
        self.api_client = api_client

    def setup(self) -> SetupServiceResult:
        params = AttributeSetApiParam(
            page=1,
            page_size=5
        )
        elastic_suite_result:AttributeSetApiResponse = self.api_client.get_attribute_set(params)
        return SetupServiceResult(
            message=f"{len(elastic_suite_result.attributes)} attributes received"
        )
