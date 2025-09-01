from typing import Annotated, List
from fastapi import Depends

from fields import AttributeField
from models import SearchContext, AttributeSetDto, ElasticSuiteAttributeSet
from services import DatabaseAttributesSetupService
from agents import AttributeSetExtractionAgent
from dependencies import inject_attribute_database_service

class AttributeDetectionManager:

    def __init__(
            self,
            attribute_set_db_service : Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_set_extraction_agent: Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)]):
        self.attribute_set_db_service = attribute_set_db_service
        self.attribute_set_extraction_agent = attribute_set_extraction_agent

    def detect(self, context:SearchContext) -> SearchContext:
        # Get attribute set list
        attribute_sets:List[AttributeSetDto] = self.attribute_set_db_service.list_attribute_sets()
        context.attribute_sets = attribute_sets

        # Detect product (attribute set)
        detected_attribute_sets:AttributeField = self.attribute_set_extraction_agent.invoke(
            user_message=context.exchange,
            attribute_set=[ElasticSuiteAttributeSet(name=attr.name, description=attr.description) for attr in attribute_sets],
            product_counter_example="bicycle" # TODO
        )
        print(f"[{detected_attribute_sets.is_intent}]: {detected_attribute_sets.chain_of_thoughts}")
        context.detected_attribute_sets = detected_attribute_sets

        return context