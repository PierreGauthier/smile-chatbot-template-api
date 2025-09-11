from dataclasses import dataclass
from domain.models import RagDocumentMetadata

@dataclass
class RagDocument:
    content: str
    metadata: RagDocumentMetadata