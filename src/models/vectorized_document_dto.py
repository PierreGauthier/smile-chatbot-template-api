from typing import List, Optional

from models import Metadata

class VectorizedDocumentDto:
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