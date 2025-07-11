from typing import List, Annotated
from fastapi import Depends

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from config import Settings, get_settings
from models import RagChainResult, DocumentIdentifier, IndexFilterResult
from agents import (
    LlmAgent,
    AzureOpenAiLlmAgent,
    VectorStoreAgent,
    AzureSearchVectorStoreAgent,
)
from prompts import PromptProvider, RagMainPromptProvider, ContextualizePromptProvider

# import logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

class RagAgent:
    def __init__(self,
            settings: Annotated[Settings, Depends(get_settings)],
            llm_agent: Annotated[LlmAgent, Depends(AzureOpenAiLlmAgent)],
            vector_store_agent: Annotated[VectorStoreAgent, Depends(AzureSearchVectorStoreAgent)],
            contextualize_prompt_provider: Annotated[PromptProvider, Depends(ContextualizePromptProvider)],
            rag_prompt_provider: Annotated[PromptProvider, Depends(RagMainPromptProvider)]):
        self.settings = settings
        self.doc_ids = []
        self.chat = llm_agent.get_llm()
        self.contextualize_prompt_provider = contextualize_prompt_provider
        self.rag_prompt_provider = rag_prompt_provider
        self.vector_store_agent = vector_store_agent

    def invoke(self, input_message:str, exchange:str, index: IndexFilterResult) -> RagChainResult:

        # 1) fetch docs
        retriever = self.vector_store_agent.get_vector_store_as_retriever(index)
        docs = retriever.invoke(input_message)
        context = self.__format_docs_with_source(docs)

        # 2) fallback if no doc mentions the keyword
        if not docs:
            answer_text = "Sorry, I don't know how to answer that question."
            return RagChainResult(answer=AIMessage(content=answer_text), documents=[])

        # 3) otherwise run the normal RAG prompt
        rag_prompt = self.rag_prompt_provider.get_prompt(exchange=exchange)
        ai_message: AIMessage = (
            rag_prompt
            | self.chat
        ).invoke({"question": input_message, "context": context})

        return RagChainResult(answer=ai_message, documents=self.doc_ids)
    
    def __format_docs_with_source(self, docs: List[Document]) -> str:
        return "\n\n".join(self.__format_doc_with_source(doc) for doc in docs)
    
    def __format_doc_with_source(self, doc: Document) -> str:
        if "id" in doc.metadata.keys():
            doc_id = DocumentIdentifier(id=doc.metadata['id'], doc_type=doc.metadata['doc_type'])
            self.doc_ids.append(doc_id)
            
        return doc.page_content
