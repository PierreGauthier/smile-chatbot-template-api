from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from agents import (
    SummarizeExchangeAgent,
    BasicPydanticChain,
    AttributeSetExtractionAgent,
    FilterExtractionAgent
)
from services import DatabaseHistoryService, ChatService, DatabaseAttributesSetupService, DatabaseRequestService
from models import (
    ChatServiceResult, 
    AttributeSetDto,
    ElasticSuiteAttributeSet,
    AttributeFilterDto,
    ChatMessage,
    UserRequestDto
)
from fields import AttributeField
from dependencies import inject_history_service, inject_attribute_database_service, inject_request_service

class ConversationalSearchService(ChatService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            attribute_set_db_service : Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_set_extraction_agent: Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)],
            filters_extraction_agent: Annotated[FilterExtractionAgent, Depends(FilterExtractionAgent)],
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(SummarizeExchangeAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service)],
            request_db_service: Annotated[DatabaseRequestService, Depends(inject_request_service)]):
        self.settings = settings
        self.attribute_set_db_service = attribute_set_db_service
        self.attribute_set_extraction_agent = attribute_set_extraction_agent
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent
        self.filters_extraction_agent = filters_extraction_agent
        self.request_db_service = request_db_service

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> ChatServiceResult:

        # Insert user message and get the message history
        current_session_id = session_id
        if current_session_id:
            new_message = ChatMessage.build_human_message(
                session_id=current_session_id,
                user_id=user_id, 
                content=input_message
            )
            self.history_db_service.upsert_message(new_message)
        else:
            new_message:ChatMessage = self.history_db_service.create_message_thread(user_id=user_id, message=input_message)
            current_session_id = new_message.session_id
        message_thread:List[ChatMessage] = self.history_db_service.get_message_thread(user_id=user_id, session_id=current_session_id)

        # Summarize exchange
        exchange = input_message
        if len(message_thread) > 1:
            # DEBUG
            for msg in message_thread:
                print(f"---{msg.data.content}")

            exchange = self.summarize_exchange_agent.invoke(message_thread)
            print(exchange)
        
        # Get requests
        requests:List[UserRequestDto] = self.request_db_service.get_requests(
            user_id=user_id, 
            session_id=current_session_id
        ) if session_id else []

        # Get attribute set list
        attribute_sets:List[AttributeSetDto] = self.attribute_set_db_service.list_attribute_sets()

        # Detect product (attribute set)
        detected_attribute_sets:AttributeField = self.attribute_set_extraction_agent.invoke(
            user_message=exchange,
            attribute_set=[ElasticSuiteAttributeSet(name=attr.name, description=attr.description) for attr in attribute_sets],
            product_counter_example="bicycle" # TODO
        )
        print(f"[{detected_attribute_sets.is_intent}]: {detected_attribute_sets.chain_of_thoughts}")

        # Build a request for each product that the user is searching for
        request_chain_results = []
        for product in detected_attribute_sets.products:
            # Get the filter list of the product
            attribute_set_name = next((attr for attr in attribute_sets if attr.name == product), None)
            if attribute_set_name:
                filters:List[AttributeFilterDto] = self.attribute_set_db_service.get_filters(attribute_set_name.attribute_set_id)
                result = self.filters_extraction_agent.invoke(exchange=exchange, filters=filters)
                request_chain_results.append(result)
            # if not attribute_set_name:
                # return ChatServiceResult(
                #     user_id=user_id,
                #     session_id=session_id,
                #     answer="Sorry, I couldn't find the product you are searching for.",
                #     sources=[]
                # )

        # filters:List[AttributeFilterDto] = self.attribute_set_db_service.get_filters(attribute_set_name.attribute_set_id)
        # result = self.filters_extraction_agent.invoke(exchange=exchange, filters=filters)

        return ChatServiceResult(
            user_id=user_id,
            session_id=session_id,
            answer= str(detected_attribute_sets.products),#f"Found {len(filters)} filters",
            sources=[]
        )
    