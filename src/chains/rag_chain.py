from typing import List, Annotated
from fastapi import Depends

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import AIMessage

from config import Settings, get_settings
from models import RagChainResult, DocumentIdentifier, IndexFilterResult
from services import (
    LlmService,
    AzureOpenAiLlmService,
    VectorStoreService,
    AzureSearchVectorStoreService,
)
from prompts import PromptProvider, RagMainPromptProvider, ContextualizePromptProvider

# import logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

class RagChain:
    def __init__(self,
            settings: Annotated[Settings, Depends(get_settings)],
            llm_service: Annotated[LlmService, Depends(AzureOpenAiLlmService)],
            vector_store_service: Annotated[VectorStoreService, Depends(AzureSearchVectorStoreService)],
            contextualize_prompt_provider: Annotated[PromptProvider, Depends(ContextualizePromptProvider)],
            rag_prompt_provider: Annotated[PromptProvider, Depends(RagMainPromptProvider)]):
        self.settings = settings
        self.doc_ids = []
        self.chat = llm_service.get_llm()
        self.contextualize_prompt_provider = contextualize_prompt_provider
        self.rag_prompt_provider = rag_prompt_provider
        self.vector_store_service = vector_store_service

    def invoke(self, input_message:str, exchange:str, index: IndexFilterResult) -> RagChainResult:

        retriever = self.vector_store_service.get_vector_store_as_retriever(index)
        contextualize_prompt = self.contextualize_prompt_provider.get_prompt()
        contextualize_q_chain = contextualize_prompt | self.chat | StrOutputParser()
        rag_prompt:ChatPromptTemplate = self.rag_prompt_provider.get_prompt(exchange) 
        
        rag_chain = (
            RunnablePassthrough.assign(
                context=contextualize_q_chain | retriever | self.__format_docs_with_source
            )
            | rag_prompt
            | self.chat
        )

        ai_message: AIMessage = rag_chain.invoke({"question": input_message})
        return RagChainResult(answer=ai_message, documents=self.doc_ids)
    
    def __format_docs_with_source(self, docs: List[Document]) -> str:
        return "\n\n".join(self.__format_doc_with_source(doc) for doc in docs)
    
    def __format_doc_with_source(self, doc: Document) -> str:
        if "id" in doc.metadata.keys():
            doc_id = DocumentIdentifier(id=doc.metadata['id'], doc_type=doc.metadata['doc_type'])
            self.doc_ids.append(doc_id)
            
        return doc.page_content
