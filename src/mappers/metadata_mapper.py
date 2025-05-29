from models import Metadata

class MetadataMapper:
    def to_dict(object:Metadata):
        return {
            "sourceFile": object.sourceFile,
            "contentType": object.contentType,
            "pageNumber": object.pageNumber
        }
        
    def from_dict(metadata: dict):
        return Metadata(
            sourceFile = metadata["sourceFile"],
            contentType = metadata["contentType"],
            pageNumber = metadata["pageNumber"]
        )