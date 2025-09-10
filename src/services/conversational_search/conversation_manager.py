from typing import Annotated, List
from fastapi import Depends

from models import SearchContext, ChatMessage
from agents import ExchangeSummarizerAgent, BasicPydanticChain
from services import DatabaseHistoryService
from dependencies import inject_history_service, inject_logger
from logger import ContextLogger

class ConversationManager:
    def __init__(
            self,
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(ExchangeSummarizerAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service)],
            logger: Annotated[ContextLogger, Depends(inject_logger)]):
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent
        self.logger = logger 
        
    def insert_or_create_thread(self, context:SearchContext) -> SearchContext:
        # Insert user message and get the message history
        current_session_id = context.session_id
        if current_session_id:
            new_message = ChatMessage.build_human_message(
                session_id=current_session_id,
                user_id=context.user_id, 
                content=context.input_message
            )
            self.history_db_service.upsert_message(new_message)
            context.session_id = current_session_id
            self.logger.debug_context(f"New HUMAN message inserted: {context.input_message}", context)
        else:
            new_message:ChatMessage = self.history_db_service.create_message_thread(
                user_id=context.user_id, 
                message=context.input_message
            )
            current_session_id = new_message.session_id
            context.session_id = current_session_id
            self.logger.debug_context(f"New thread created: {context.input_message}", context)
        message_thread:List[ChatMessage] = self.history_db_service.get_message_thread(
            user_id=context.user_id, 
            session_id=current_session_id
        )
        context.message_thread = message_thread
        return context
    
    def summarize_exchange(self, context:SearchContext) -> SearchContext:
        # Summarize exchange
        exchange = self.__summarize_exchange(context)
        context.exchange = exchange
        return context
    
    def store_ai_answer(self, context:SearchContext):
        self.history_db_service.upsert_message(message=ChatMessage.build_ai_message(
            user_id=context.user_id,
            session_id=context.session_id,
            content=context.ai_answer
        ))
        self.logger.debug_context(f"New AI message inserted: {context.ai_answer}", context)
            
    # PRIVATE 

    def __summarize_exchange(self, context:SearchContext):
        exchange = context.input_message
        if len(context.message_thread) > 1:
            exchange = self.summarize_exchange_agent.invoke(context.message_thread)
            self.logger.debug_context(message=f"Exchange summary: {exchange}", context=context)
        else:
            self.logger.debug_context(message=f"Input message: {exchange}", context=context)

        return exchange