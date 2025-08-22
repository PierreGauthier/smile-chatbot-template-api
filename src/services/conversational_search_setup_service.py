from typing import Annotated
from fastapi import Depends

from models import (
    AttributeSetApiParam, 
    AttributeSetApiResponse,
    SetupServiceResult
)
from api_clients import ElasticSuiteAttributeSetClient
from agents import AttributeSetExtractionAgent
from services import DatabaseAttributesSetupService
from dependencies import inject_attribute_database_service

class ConversationalSearchSetupService:

    def __init__(
            self,
            api_client:Annotated[ElasticSuiteAttributeSetClient, Depends(ElasticSuiteAttributeSetClient)],
            attribute_db_service: Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_extraction_agent:Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)]):
        self.api_client = api_client
        self.attribute_extraction_agent = attribute_extraction_agent
        self.attribute_db_service = attribute_db_service

    def setup(self) -> SetupServiceResult:
        params = AttributeSetApiParam(
            page=1,
            page_size=4
        )
        elastic_suite_result:AttributeSetApiResponse = self.api_client.get_attribute_set(params)
        for attribute_set in elastic_suite_result.attributes:
            self.attribute_db_service.insert_attribute_set(attribute_set)

        return SetupServiceResult(
            message=f"{len(elastic_suite_result.attributes)} attributes received"
        )
    


