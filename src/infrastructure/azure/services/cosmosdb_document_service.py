from typing import Annotated
from fastapi import Depends

from domain.models import RagDocument, RagDocumentMetadata
from domain.services.database import DatabaseDocumentService

from infrastructure.azure.services import CosmosDb

from config import Settings, get_settings

class CosmosDbDocumentService(DatabaseDocumentService):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.database = CosmosDb(
            container=settings.azure_cosmos_document_container,
            partition_key=settings.azure_cosmos_document_partition_key,
            settings=settings
        )
    
    def get_document(self, doc_type:str, document_id:str) -> RagDocument: 
        container = self.database.get_container()
        document = container.read_item(item=document_id, partition_key=doc_type)
        return self.__parse_document_data(document)
    
    def __parse_document_data(self, document: dict):
        metadata_dict = document['metadata']
        return RagDocument(
            content = document["content"],
            metadata=RagDocumentMetadata(
                id = document["id"],
                doc_type = document["doc_type"],
                sourceName = metadata_dict["sourceName"],
                contentType = metadata_dict["contentType"],
                pageNumber = metadata_dict["pageNumber"],
                documentUrl = metadata_dict["documentUrl"]
            )
        )