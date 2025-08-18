from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from agents import (
    SummarizeExchangeAgent,
    RagAgent,
    BasicPydanticChain,
    IntentExtractionAgent
)
from services import DatabaseDocumentService, DatabaseHistoryService, ChatService
from models import (
    ChatServiceResult, 
    ChatMessage,
    IndexFilterResult,
    Source,
    RagDocument
)
from fields import IntentDefinitionField
from dependencies import inject_history_service, inject_document_service

class DefaultRagChatService(ChatService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            intent_extraction_agent: Annotated[BasicPydanticChain, Depends(IntentExtractionAgent)],
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(SummarizeExchangeAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service)]):
        self.settings = settings
        self.intent_extraction_agent = intent_extraction_agent
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> ChatServiceResult:

        # (0) Detect intent
        intent:IntentDefinitionField = self.intent_extraction_agent.invoke(input_message)
        print(f"[{intent.is_intent}]: {intent.chain_of_thoughts}")
    