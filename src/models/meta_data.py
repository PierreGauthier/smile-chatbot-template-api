from typing import Optional

class Metadata:
    def __init__(self, 
            sourceFile: str, 
            contentType: str, 
            filename: Optional[str] = None, 
            filetype: Optional[str] = None,
            pageNumber: Optional[int] = None):
        self.sourceFile = sourceFile
        self.contentType = contentType 
        self.filename = filename
        self.filetype = filetype
        self.pageNumber = pageNumber

    def to_dict(self):
        return {
            "sourceFile": self.sourceFile,
            "contentType": self.contentType,
            "pageNumber": self.pageNumber
        }
    
    @staticmethod
    def from_dict(metadata: dict):
        return Metadata(
            sourceFile = metadata["sourceFile"],
            contentType = metadata["contentType"],
            pageNumber = metadata["pageNumber"]
        )