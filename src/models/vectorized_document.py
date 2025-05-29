from typing import List, Optional
from dataclasses import dataclass

from models import Metadata

@dataclass
class VectorizedDocument:
    id: Optional[str]
    doc_type: str
    content: str
    metadata: Metadata
    content_vector:List[float]

    @staticmethod
    def from_dict(document: dict):      
        
        return VectorizedDocument(
            id = document["id"],
            doc_type = document["doc_type"],
            content = document["content"],
            content_vector = document["content_vector"],
            metadata = Metadata.from_dict(document["metadata"])
        )