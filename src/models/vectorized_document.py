from typing import List, Optional

from models import Metadata

class VectorizedDocument:
    def __init__(self, 
            id: Optional[str],
            doc_type: str,
            content: str,
            metadata: Metadata,
            content_vector:List[float]):
        self.id = id
        self.doc_type = doc_type
        self.content = content
        self.metadata = metadata
        self.content_vector = content_vector

    @staticmethod
    def from_dict(document: dict):      
        
        return VectorizedDocument(
            id = document["id"],
            doc_type = document["doc_type"],
            content = document["content"],
            content_vector = document["content_vector"],
            metadata = Metadata.from_dict(document["metadata"])
        )