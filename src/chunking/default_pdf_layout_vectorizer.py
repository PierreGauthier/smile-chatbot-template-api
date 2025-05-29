import json
from typing import List, Dict

from chunking import DocumentVectoriser

class DefaultPdfLayoutVectoriser(DocumentVectoriser):
    """Vectorize the content extracted from LAYOUT result file from Azure Document Inteligence"""
    def __init__(self, 
            source_filename:str, # layout (JSON) file
            document_title:str, 
            key_words:List[str], 
            doc_type:str):
        super().__init__(source_filename=source_filename, document_title=document_title,key_words=key_words, doc_type=doc_type, page=0)

    def chunk(self) -> Dict[int, List[str]]:
        with open(self.source_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        results = json_data["analyzeResult"]
        paragraphs = results["paragraphs"]

        content_by_page = {}

        for p in paragraphs:
            if 'role' in p:
                continue

            page_number = p['boundingRegions'][0]['pageNumber'] if 'boundingRegions' in p and p['boundingRegions'] else 0

            content = p['content']
            content = content.replace(':selected:', '').replace(':unselected:', '')

            if page_number in content_by_page:
                content_by_page[page_number].append(content)
            else:
                content_by_page[page_number] = [content]
        
        return content_by_page