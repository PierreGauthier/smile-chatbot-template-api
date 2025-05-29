from typing import List
from dataclasses import dataclass
from langchain_core.messages import AIMessage

from models import DocumentIdentifier

@dataclass
class RagChainResult:
    answer: AIMessage
    documents: List[DocumentIdentifier]