from models import VectorizedDocument, Metadata

class GoogleCloudStorageDocumentMapper:

    @staticmethod
    def from_dict(document: dict):        
        return VectorizedDocument(
            id = document['metadata']['id'],
            doc_type = document['metadata']["doc_type"],
            content = document['metadata']["page_content"],
            content_vector = [],#document["content_vector"],
            metadata = Metadata(
                sourceName=document['metadata']["sourceName"],
                contentType=document['metadata']["contentType"],
                pageNumber=document['metadata']["pageNumber"],
                documentUrl=document['metadata']["documentUrl"],
            )
        )