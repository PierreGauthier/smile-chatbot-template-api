from typing import Annotated, List
from fastapi import Depends

from models import SearchContext, ChatMessage
from agents import ExchangeSummarizerAgent, BasicPydanticChain
from services import DatabaseHistoryService
from dependencies import inject_history_service

class ConversationManager:
    def __init__(
            self,
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(ExchangeSummarizerAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service)]):
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent

    def insert_or_create_thread(self, context:SearchContext) -> SearchContext:

        # Insert user message and get the message history
        current_session_id, message_thread = self.__get_history_thread(
            input_message=context.input_message,
            user_id=context.user_id, 
            session_id=context.session_id
        )
        context.session_id = current_session_id
        context.message_thread = message_thread
        return context
    
    def summarize_exchange(self, context:SearchContext) -> SearchContext:
        # Summarize exchange
        exchange = self.__summarize_exchange(input_message=context.input_message, message_thread=context.message_thread)
        context.exchange = exchange
        return context
    
    def store_ai_answer(self, context:SearchContext):
        self.history_db_service.upsert_message(message=ChatMessage.build_ai_message(
            user_id=context.user_id,
            session_id=context.session_id,
            content=context.ai_answer
        ))
    
    # PRIVATE 

    def __summarize_exchange(self, input_message:str, message_thread:List[ChatMessage]):
        exchange = input_message
        if len(message_thread) > 1:
            # DEBUG
            for msg in message_thread:
                print(f"---{msg.data.content}")

            exchange = self.summarize_exchange_agent.invoke(message_thread)
            print(exchange)
        return exchange

    def __get_history_thread(self, input_message:str, user_id:str, session_id):
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
        return current_session_id, message_thread