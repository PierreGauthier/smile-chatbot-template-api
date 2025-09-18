from typing import Annotated, List
from fastapi import Depends
from functools import partial

from domain.fields import AttributeField
from domain.models import SearchContext, AttributeSetDto, ElasticSuiteAttributeSet
from domain.services.database import DatabaseAttributesSetupService
from domain.logger import ContextLogger

from application.agents import AttributeSetExtractionAgent

from dependencies import inject_attribute_database_service, inject_logger

class AttributeDetectionManager:

    def __init__(
            self,
            attribute_set_db_service : Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_set_extraction_agent: Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="AttributeDetectionManager"))]):
        self.attribute_set_db_service = attribute_set_db_service
        self.attribute_set_extraction_agent = attribute_set_extraction_agent
        self.logger = logger

    def detect(self, context:SearchContext) -> SearchContext:
        # Get attribute set list
        attribute_sets:List[AttributeSetDto] = self.attribute_set_db_service.list_attribute_sets()
        context.attribute_sets = attribute_sets

        # Detect product (attribute set)
        detected_attribute_sets:AttributeField = self.attribute_set_extraction_agent.invoke(
            user_message=context.exchange,
            attribute_set=[ElasticSuiteAttributeSet(name=attr.code, description=attr.description) for attr in attribute_sets],
            product_counter_example="bicycle" # TODO
        )
        
        self.logger.debug_context(
            message=f"[{detected_attribute_sets.is_intent}]: {detected_attribute_sets.chain_of_thoughts}",
            context=context
        )
        if detected_attribute_sets.is_intent:
            products = ", ".join(detected_attribute_sets.products)
            self.logger.debug_context(
                message=f"Attribute sets: {products}",
                context=context
            )
        
        context.detected_attribute_sets = detected_attribute_sets

        return context