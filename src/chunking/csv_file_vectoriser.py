import csv
from typing import List, Dict
from abc import abstractmethod

from chunking import DocumentVectoriser

class CsvFileVectoriser(DocumentVectoriser):
    def __init__(self, 
            source_filename:str, 
            document_title:str, 
            key_words:List[str], 
            doc_type:str, 
            page:int = 1, 
            start_line = 1):
        super().__init__(source_filename=source_filename, document_title=document_title,key_words=key_words, doc_type=doc_type, page=page)
        self.start_line = start_line

    def chunk(self) -> Dict[int, List[str]]:
        """Generic method for line-by-line chunking strategy"""
        lines = { self.page: []}
        with open(self.source_file_path, 'r', encoding='utf-8') as file:
            for i in range(self.start_line):
                next(file)
            reader = csv.reader(file, delimiter=',')            
            for row in reader:
                text = self.build_line(row)
                #print(text) 
                lines[self.page].append(text)
        return lines

    @abstractmethod
    def build_line(self, row:list[str]):
        pass

    def parse_last_column(self, value: str) -> List[int]:
        if ',' in value:
            return [int(x.strip()) for x in value.split(',')]
        return [int(value)]