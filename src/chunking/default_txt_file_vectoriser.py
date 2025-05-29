from typing import List, Dict

from chunking import ITxtFileVectoriser

class DefaultTxtFileVectoriser(ITxtFileVectoriser):
    def __init__(self, source_filename:str, document_title:str, key_words:List[str], doc_type:str, page:int = 1, chunk_size=512):
        super().__init__(source_filename=source_filename, document_title=document_title,key_words=key_words, doc_type=doc_type, page=page, chunk_size=chunk_size)

    def chunk(self) -> Dict[int, List[str]]:
        with open(self.source_file_path, 'r', encoding='utf-8') as file:
            content = file.read()        
        chunks = { self.page: [] }
        for i in range(0, len(content), self.chunk_size):
            chunk = content[i : i + self.chunk_size]
            chunks[self.page].append(chunk)
        return chunks
