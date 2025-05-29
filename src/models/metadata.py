from dataclasses import dataclass

@dataclass
class Metadata:
    sourceFile: str
    contentType: str 
    pageNumber: int
    document_url: str

    def to_dict(self):
        return {
            "sourceFile": self.sourceFile,
            "contentType": self.contentType,
            "pageNumber": self.pageNumber,
            "document_url": self.document_url
        }
    
    @staticmethod
    def from_dict(metadata: dict):
        return Metadata(
            sourceFile = metadata["sourceFile"],
            contentType = metadata["contentType"],
            pageNumber = metadata["pageNumber"],
            document_url = metadata["document_url"]
        )