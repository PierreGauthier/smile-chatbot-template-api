from typing import List
from langchain_core.messages import AIMessage
from models import DocumentIdentifier

class RagChainResult:
    def __init__(self, answer: AIMessage, documents: List[DocumentIdentifier]):
        self.answer = answer
        self.documents = documents