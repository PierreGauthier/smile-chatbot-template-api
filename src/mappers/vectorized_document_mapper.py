from mappers import MetadataMapper
from models import VectorizedDocumentDto
    
class VectorizedDocumentMapper:
    def from_dict(document: dict):      
        
        return VectorizedDocumentDto(
            id = document["id"],
            doc_type = document["doc_type"],
            content = document["content"],
            content_vector = document["content_vector"],
            metadata = MetadataMapper.from_dict(document["metadata"])
        )