from typing import Annotated
from fastapi import Depends

from domain.models import (
    AttributeSetApiParam, 
    AttributeSetApiResponse,
    SetupServiceResult
)
from domain.api_client.configuration_client import ConfigurationClient
from domain.services.database import DatabaseAttributesSetupService

from dependencies import inject_attribute_database_service, inject_configuration_client
from application.agents import AttributeSetExtractionAgent

class ConversationalSearchSetupService:
    """Configures conversational search by syncing attribute sets from the API into the local store."""

    def __init__(
            self,
            api_client:Annotated[ConfigurationClient, Depends(inject_configuration_client)],
            attribute_db_service: Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_extraction_agent:Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)]):
        """
        Initialize the setup service with the required dependencies.

        Args:
            api_client: Client used to fetch attribute sets from the configuration API.
            attribute_db_service: Persistence service that inserts attribute sets into the database.
            attribute_extraction_agent: Agent responsible for extracting attribute sets when needed.
        """
        self.api_client = api_client
        self.attribute_extraction_agent = attribute_extraction_agent
        self.attribute_db_service = attribute_db_service

    def setup(self) -> SetupServiceResult:
        """
        Fetch attribute sets from the external API and persist them locally.

        Returns:
            Result detailing how many attribute sets were retrieved.
        """
        params = AttributeSetApiParam(
            page=1,
            page_size=10
        )
        elastic_suite_result:AttributeSetApiResponse = self.api_client.get_attribute_set(params)
        for attribute_set in elastic_suite_result.attributes:
            self.attribute_db_service.insert_attribute_set(attribute_set)

        return SetupServiceResult(
            message=f"{len(elastic_suite_result.attributes)} attributes received"
        )
