from dataclasses import dataclass

@dataclass
class RagDocumentMetadata:
    id: str
    doc_type: str
    sourceName: str
    contentType: str 
    pageNumber: int
    documentUrl: str
