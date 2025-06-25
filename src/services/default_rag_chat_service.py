from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from chains import (
    SummarizeExchangeChain,
    RagChain,
    BasicPydanticChain,
    IntentExtractionChain
)
from services import (
    DatabaseDocumentService, 
    CosmosDbDocumentService, 
    DatabaseHistoryService,
    CosmosDbHistoryService,
    ChatService
)
from models import (
    RagChatServiceResult, 
    ChatMessage,
    IndexFilterResult,
    DocumentSource,
    VectorizedDocument
)
from fields import IntentDefinitionField

class DefaultRagChatService(ChatService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            rag_chain: Annotated[RagChain, Depends(RagChain)],
            document_db_service: Annotated[DatabaseDocumentService, Depends(CosmosDbDocumentService)],
            intent_extraction_chain: Annotated[BasicPydanticChain, Depends(IntentExtractionChain)],
            summarize_exchange_chain : Annotated[SummarizeExchangeChain, Depends(SummarizeExchangeChain)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(CosmosDbHistoryService)]):
        self.settings = settings
        self.intent_extraction_chain = intent_extraction_chain
        self.rag_chain = rag_chain
        self.document_db_service = document_db_service
        self.history_db_service = history_db_service
        self.summarize_exchange_chain = summarize_exchange_chain

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> RagChatServiceResult:
        """Get RAG response"""

        # (0) Detect intent
        intent:IntentDefinitionField = self.intent_extraction_chain.invoke(input_message)
        print(f"[{intent.is_intent}]: {intent.chain_of_thoughts}")

        # (1) Get the message history (or create a new one)
        (current_session_id, message_thread) = self.__get_messages_thread(user_id=user_id, session_id=session_id, message=input_message)

        # (2) Summarize exchange
        exchange = None
        if len(message_thread) > 1:
            for msg in message_thread:
                print(f"---{msg.data.content}")

            exchange = self.summarize_exchange_chain.invoke(message_thread[:-1]) # Not the last (new) one
            print(exchange)

        # (3) RAG
        index = IndexFilterResult(index_name=self.settings.azure_search_index)
        rag_result = self.rag_chain.invoke(exchange=exchange, input_message=input_message, index=index)        
        ai_answer = rag_result.answer.content
        document_references = [
            self.document_db_service.get_document(doc_type=doc_id.doc_type, document_id=doc_id.id) 
            for doc_id in rag_result.documents if doc_id.doc_type and doc_id.id
        ]
        
        # (4) Group sources by document name:
        sources = [] if not intent.is_intent else self.build_sources(document_references)

        # (5) Insert AI-RAG response
        ai_response = ChatMessage.build_ai_message(
            session_id=current_session_id,
            user_id=user_id, 
            content=ai_answer
        )
        self.history_db_service.upsert_message(ai_response)
        
        return RagChatServiceResult(
            user_id=user_id, 
            session_id=current_session_id, 
            answer=ai_answer,
            sources=sources
        ) 

    ### PRIVATE

    def __get_messages_thread(self, user_id:str, session_id:str|None, message:str):
        if session_id:
            new_message = ChatMessage.build_human_message(
                session_id=session_id,
                user_id=user_id, 
                content=message
            )
            self.history_db_service.upsert_message(new_message)
            thread:List[ChatMessage] = self.history_db_service.get_message_thread(user_id=user_id, session_id=session_id)
            return (session_id, thread)
        else: 
            new_message:ChatMessage = self.history_db_service.create_message_thread(user_id=user_id, message=message)
            return (new_message.session_id, [new_message])
        
    def build_sources(self, document_references:List[VectorizedDocument]):
        sources: List[DocumentSource] = []
        seen: set[tuple[str, int]] = set()

        for doc in document_references:
            key = (doc.metadata.sourceName, doc.metadata.pageNumber)
            if key not in seen:
                seen.add(key)
                sources.append(
                    DocumentSource(
                        document_name=doc.metadata.sourceName,
                        document_type=doc.doc_type,
                        page_number=doc.metadata.pageNumber,
                        document_url=doc.metadata.documentUrl,
                    )
                )
        return sources
