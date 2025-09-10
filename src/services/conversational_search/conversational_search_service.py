from typing import Annotated
from fastapi import Depends
from config import Settings, get_settings
from functools import partial

from langchain_core.globals import set_verbose, set_debug

from services import (
    ConversationManager,
    RequestManager,
    AttributeDetectionManager,
    SearchManager,
    SearchService, 
)
from models import SearchContext, SearchServiceResult
from logger import ContextLogger
from dependencies import inject_logger

class ConversationalSearchService(SearchService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            conversation_manager:Annotated[ConversationManager, Depends(ConversationManager)],
            request_manager:Annotated[RequestManager, Depends(RequestManager)],
            attribute_set_manager:Annotated[AttributeDetectionManager, Depends(AttributeDetectionManager)],
            search_manager:Annotated[SearchManager, Depends(SearchManager)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="ConversationalSearchService"))]):
        self.settings = settings
        self.conversation_manager = conversation_manager
        self.request_manager = request_manager
        self.attribute_set_manager = attribute_set_manager
        self.search_manager = search_manager
        self.logger = logger

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> SearchServiceResult:
        
        context = SearchContext(
            input_message=input_message, 
            user_id=user_id, 
            session_id=session_id, 
            is_first_call= not session_id
        )
        # (1) Get (or create) message thread
        context = self.conversation_manager.insert_or_create_thread(context)
        
        # (2) Summarize exchange
        context = self.conversation_manager.summarize_exchange(context)

        # (3) Get requests
        context = self.request_manager.get_requests(context)

        # (4) Get attributes from DB and detect from user message
        context = self.attribute_set_manager.detect(context)
        if not context.detected_attribute_sets.products:
            return SearchServiceResult(
                user_id=user_id,
                session_id=context.session_id,
                answer="Sorry, we don't sell this product here.", # -> TODO: response agent
                products=[]
            )

        # (5) Build a request for each product that the user is searching for
        context = self.request_manager.build_requests(context)

        # (6) Upsert the requests
        self.request_manager.upsert_requests(context)

        # (7) If no product or filter detected -> TODO: response agent
        if not context.request_chain_results:
            return SearchServiceResult(
                user_id=user_id,
                session_id=context.session_id,
                answer="Sorry, I couldn't find the product(s) you are searching for.",
                products=[]
            )

        # (8) Search OR ask for filters
        context = self.search_manager.search(context)
        
        # (9) Insert the AI message in the DB
        self.conversation_manager.store_ai_answer(context)

        self.logger.info_context("Search workflow complete.", context)

        return SearchServiceResult(
            user_id=context.user_id,
            session_id=context.session_id,
            answer=context.ai_answer,
            products=context.search_result
        )