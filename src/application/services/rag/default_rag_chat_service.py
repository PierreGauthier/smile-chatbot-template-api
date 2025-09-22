from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from domain.services.database import DatabaseDocumentService, DatabaseHistoryService
from domain.services.chatbot import ChatService
from domain.models import (
    ChatServiceResult, 
    IndexFilterResult,
    Source,
    RagDocument
)
from domain.fields import IntentDefinitionField

from application.agents import (
    ExchangeSummarizerAgent,
    RagAgent,
    BasicPydanticChain,
    IntentExtractionAgent
)
from application.models import RagChatMessage

from dependencies import inject_history_service_for_RAG, inject_document_service

class DefaultRagChatService(ChatService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            rag_agent: Annotated[RagAgent, Depends(RagAgent)],
            document_db_service: Annotated[DatabaseDocumentService, Depends(inject_document_service)],
            intent_extraction_agent: Annotated[BasicPydanticChain, Depends(IntentExtractionAgent)],
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(ExchangeSummarizerAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service_for_RAG)]):
        self.settings = settings
        self.intent_extraction_agent = intent_extraction_agent
        self.rag_agent = rag_agent
        self.document_db_service = document_db_service
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> ChatServiceResult:
        """Get RAG response"""

        # (0) Detect intent
        intent:IntentDefinitionField = self.intent_extraction_agent.invoke(input_message)
        print(f"[{intent.is_intent}]: {intent.chain_of_thoughts}")

        # (1) Insert user message and get the message history
        current_session_id = session_id
        if current_session_id:
            new_message = RagChatMessage.build_human_message(
                session_id=current_session_id,
                user_id=user_id, 
                content=input_message
            )
            self.history_db_service.upsert_message(new_message)
        else:
            new_message:RagChatMessage = self.history_db_service.create_message_thread(user_id=user_id, message=input_message)
            current_session_id = new_message.session_id
        message_thread:List[RagChatMessage] = self.history_db_service.get_message_thread(user_id=user_id, session_id=current_session_id)

        # (2) Summarize exchange
        exchange = input_message
        if len(message_thread) > 1:
            # DEBUG
            for msg in message_thread:
                print(f"---{msg.data.content}")

            exchange = self.summarize_exchange_agent.invoke(message_thread)
            print(exchange)

        # (3) RAG
        index = IndexFilterResult(index_name=self.settings.gcp_vertex_vector_index_id)
        rag_result = self.rag_agent.invoke(exchange=exchange, input_message=input_message, index=index)        
        ai_answer = rag_result.answer.content
        document_references = [
            self.document_db_service.get_document(doc_type=doc_id.doc_type, document_id=doc_id.id) 
            for doc_id in rag_result.documents if doc_id.doc_type and doc_id.id
        ]
        
        # (4) Group sources by document name:
        sources = [] if not intent.is_intent else self.__build_sources(document_references)
        
        # (5) Insert AI-RAG response
        ai_response = RagChatMessage.build_ai_message(
            session_id=current_session_id,
            user_id=user_id, 
            content=ai_answer,
            sources=sources
        )
        self.history_db_service.upsert_message(ai_response)
        
        return ChatServiceResult(
            user_id=user_id, 
            session_id=current_session_id, 
            answer=ai_answer,
            sources=sources
        ) 

    ### PRIVATE
        
    def __build_sources(self, document_references:List[RagDocument]):
        sources: List[Source] = []
        seen: set[tuple[str, int]] = set()

        for doc in document_references:
            key = (doc.metadata.sourceName, doc.metadata.pageNumber)
            if key not in seen:
                seen.add(key)
                sources.append(
                    Source(
                        name=doc.metadata.sourceName,
                        type=doc.metadata.doc_type,
                        page_number=doc.metadata.pageNumber,
                        address=doc.metadata.documentUrl,
                    )
                )
        return sources
