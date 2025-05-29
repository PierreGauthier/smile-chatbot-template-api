from typing import List

from chunking import DocumentVectoriser

class ITxtFileVectoriser(DocumentVectoriser):
    def __init__(self, source_filename:str, document_title:str, key_words:List[str], doc_type:str, chunk_size=512):
        super().__init__(source_filename=source_filename, document_title=document_title,key_words=key_words, doc_type=doc_type, page=1)
        self.chunk_size = chunk_size