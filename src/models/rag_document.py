from dataclasses import dataclass
from models import RagDocumentMetadata

@dataclass
class RagDocument:
    content: str
    metadata: RagDocumentMetadata