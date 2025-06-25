from dataclasses import dataclass

@dataclass
class Metadata:
    sourceName: str
    contentType: str 
    pageNumber: int
    documentUrl: str

    def to_dict(self):
        return {
            "sourceName": self.sourceName,
            "contentType": self.contentType,
            "pageNumber": self.pageNumber,
            "documentUrl": self.documentUrl
        }
    
    @staticmethod
    def from_dict(metadata: dict):
        return Metadata(
            sourceName = metadata["sourceName"],
            contentType = metadata["contentType"],
            pageNumber = metadata["pageNumber"],
            documentUrl = metadata["documentUrl"]
        )