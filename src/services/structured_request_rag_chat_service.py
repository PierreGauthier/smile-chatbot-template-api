from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from services import (
    DatabaseDocumentService, 
    CosmosDbDocumentService,
    DatabaseRequestService,
    DatabaseHistoryService,
    CosmosDbRequestService,
    CosmosDbHistoryService,
    ChatService
)
from chains import RagChain, ExtractRequestDefinitionChain
from models import (
    RagChatServiceResult, 
    IndexFilterResult,
    ChatThread,
    ChatRequest,
    RequestDefinitionField
)
from index_filter import (
    IndexFilter,
    DefaultIndexFilter
)

MAX_EXCHANGES = 2 # TODO: in config file

class StructuredRequestRagChatService(ChatService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            rag_chain: Annotated[RagChain, Depends(RagChain)],
            extract_request_definition_chain: Annotated[ExtractRequestDefinitionChain, Depends(ExtractRequestDefinitionChain)],
            document_db_service: Annotated[DatabaseDocumentService, Depends(CosmosDbDocumentService)],
            request_db_service: Annotated[DatabaseRequestService, Depends(CosmosDbRequestService)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(CosmosDbHistoryService)]):
        self.settings = settings
        self.rag_chain = rag_chain
        self.extract_request_definition_chain = extract_request_definition_chain
        self.document_db_service = document_db_service
        self.request_db_service = request_db_service
        self.history_db_service = history_db_service
        self.index_filters:List[IndexFilter] = [
            DefaultIndexFilter()
        ]

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, message: str, user_id: str, session_id: str = None) -> RagChatServiceResult:
        """Get RAG response"""

        # (1) Get the message history and request structure (or create a new one)
        chat_thread = self.__get_chat_thread(user_id=user_id, session_id=session_id)
        chat_request = self.__get_chat_request(user_id=user_id, session_id=session_id)

        # (2) Transform message into JSON request
        new_user_request:RequestDefinitionField = self.extract_request_definition_chain.try_build_request_definition(
            message, 
            chat_thread.messages
        )
        if not new_user_request:
            # The parser couldn't create the JSON request from the text
            return RagChatServiceResult(
                user_id=chat_thread.user_id,
                session_id=chat_thread.session_id, 
                answer="Something went wrong, could you please repeat your request?"
            )

        # (3) Set defaults values to the request 
        # (if "unknown" value are present)

        # (4) UPDATE request structure
        chat_request.request.merge(new_user_request)

        if not chat_request.request.is_complete():
            # (5.1) Compute number of exchanges:
            exchange_nb = len(chat_thread.messages) /2
            if exchange_nb <= MAX_EXCHANGES:
                # (5.2) Insert the exchange in the DB
                self.request_db_service.update_request(chat_request)
                self.history_db_service.insert_human_message(
                    user_id=chat_thread.user_id, 
                    session_id=chat_thread.session_id, 
                    message=message
                )
                self.history_db_service.insert_ai_message(
                    user_id=chat_thread.user_id, 
                    session_id=chat_thread.session_id, 
                    message=new_user_request.ai_response
                )
                # (5.3) Ask for more information if incomplete demand 
                return RagChatServiceResult(
                    user_id=chat_thread.user_id, 
                    session_id=chat_thread.session_id, 
                    answer=new_user_request.ai_response
                )
        
        # (6) The request is complete: Find concerned Search-INDEX
        index_result:IndexFilterResult = None
        for index_filter in self.index_filters:
            if index_filter.apply(chat_request.request):
                index_result = index_filter.get_index()
                break

        if not index_result:
            return RagChatServiceResult(
                user_id=chat_thread.user_id, 
                session_id=chat_thread.session_id, 
                answer="Sorry, we did not find any sources associated with your request. We invite you to contact the technical service."
            )
        print(f"INDEX: {index_result.index_name}")

        # (8) RAG
        rag_result = self.rag_chain.run_chain(history=chat_thread.messages, index=index_result)        
        result = f"{rag_result.answer.content}\n\n"
        document_references = [
            self.document_db_service.get_document(doc_type=doc_id.doc_type, document_id=doc_id.id) 
            for doc_id in rag_result.documents if doc_id.doc_type and doc_id.id
        ]
        
        # (9) Group sources by document name:
        sources = {}
        for document in document_references:
            if not document.metadata.sourceFile in sources:
                sources[document.metadata.sourceFile] = []
            sources[document.metadata.sourceFile].append(str(document.metadata.pageNumber))
        
        for source in sources.keys():
            pages = ", ".join(f"page {page}" for page in list(set(sources[source])))
            formatted_source = f"[{source} - ({pages})]"
            result += f"\n{formatted_source}"

        # (10) Insert AI-RAG response
        self.request_db_service.update_request(chat_request)
        self.history_db_service.insert_human_message(
            user_id=chat_thread.user_id, 
            session_id=chat_thread.session_id, 
            message=message
        )
        self.history_db_service.insert_ai_message(
            user_id=chat_thread.user_id, 
            session_id=chat_thread.session_id, 
            message=rag_result.answer.content
        )
        
        return RagChatServiceResult(
            user_id=chat_thread.user_id, 
            session_id=chat_thread.session_id, 
            answer=result
        ) 

    ### PRIVATE

    def __get_chat_thread(self, user_id:str, session_id:str|None) -> ChatThread:
        thread:ChatThread = self.history_db_service.get_chat_thread(user_id=user_id, session_id=session_id) \
            if session_id \
            else self.history_db_service.create_chat_thread(user_id=user_id)
        return thread

    def __get_chat_request(self, user_id:str, session_id:str|None) -> ChatRequest:
        request:ChatRequest = self.request_db_service.get_request(user_id=user_id, session_id=session_id) \
            if session_id \
            else self.request_db_service.create_request(user_id=user_id)
        return request