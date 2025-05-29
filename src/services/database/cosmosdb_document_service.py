from typing import Annotated
from fastapi import Depends
import uuid

from models import VectorizedDocumentDto
from mappers import VectorizedDocumentMapper, MetadataMapper
from services import DatabaseDocumentService, CosmosDbBase, CosmosDbDocumentDb

class CosmosDbDocumentService(DatabaseDocumentService):
    def __init__(self, database: Annotated[CosmosDbBase, Depends(CosmosDbDocumentDb)]):
        self.database = database
    
    def get_document(self, doc_type:str, document_id:str) -> VectorizedDocumentDto: 
        container = self.database.get_container()
        document = container.read_item(item=document_id, partition_key=doc_type)
        return VectorizedDocumentMapper.from_dict(document)
    
    def create_document_with_embedding(self, document:VectorizedDocumentDto) -> VectorizedDocumentDto:
        container = self.database.get_container()
        body_dict = {
            "id": str(uuid.uuid4()),
            "doc_type": document.metadata.contentType,
            "content": document.content,
            "content_vector": document.content_vector,
            "metadata": MetadataMapper.to_dict(document.metadata)
        }
        item_dict = container.upsert_item(
            body=body_dict
        )
        return document