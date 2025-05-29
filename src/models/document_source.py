from dataclasses import dataclass

@dataclass
class DocumentSource:
    filename:str
    page_number: int
    document_url: str