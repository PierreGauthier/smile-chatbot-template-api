from dataclasses import dataclass

@dataclass
class DocumentSource:
    document_name: str
    document_type: str
    page_number: int
    document_url: str