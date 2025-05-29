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