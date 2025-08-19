from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from agents import (
    SummarizeExchangeAgent,
    BasicPydanticChain,
    AttributeSetExtractionAgent
)
from services import DatabaseHistoryService, ChatService, DatabaseAttributesSetupService
from models import (
    ChatServiceResult, 
    AttributeSetDto,
    ElasticSuiteAttributeSet
)
from fields import AttributeField
from dependencies import inject_history_service, inject_attribute_database_service

class ConversationalSearchService(ChatService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            attribute_set_db_service : Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_set_extraction_agent: Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)],
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(SummarizeExchangeAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service)]):
        self.settings = settings
        self.attribute_set_db_service = attribute_set_db_service
        self.attribute_set_extraction_agent = attribute_set_extraction_agent
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> ChatServiceResult:

        # (0) Get attribute set list
        attribute_sets:List[AttributeSetDto] = self.attribute_set_db_service.list_attribute_sets()

        # (1) Detect product (attribute set)
        detected_attribute_set:AttributeField = self.attribute_set_extraction_agent.invoke(
            user_message=input_message,
            attribute_set=[ElasticSuiteAttributeSet(name=attr.name, description=attr.description) for attr in attribute_sets],
            product_counter_example="bicycle"
        )
        print(f"[{detected_attribute_set.is_intent}]: {detected_attribute_set.chain_of_thoughts}")

        return ChatServiceResult(
            user_id=user_id,
            session_id=session_id,
            answer=detected_attribute_set.product,
            sources=[]
        )
    