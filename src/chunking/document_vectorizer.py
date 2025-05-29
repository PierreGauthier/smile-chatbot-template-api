import json

from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from models import VectorInputPageContentType

class DocumentVectoriser(ABC):
    def __init__(self, 
            embadding_model_api_key:str, 
            source_filename:str, 
            document_title:str, 
            key_words:List[str], 
            doc_type:str, 
            page:int = 0):
        self.source_file_path = Path(source_filename) # FULL path
        self.document_title = document_title
        self.key_words = key_words
        self.page = page
        self.doc_type = doc_type
        self.embeddings:Embeddings = OpenAIEmbeddings(openai_api_key=embadding_model_api_key)

    @abstractmethod
    def chunk(self) -> Dict[int, List[str]]:
        pass

    def vectorize(self):
        chunks = self.chunk()
        self.__vectorize_chunks(chunks=chunks)

    def __save_vectorized_content_to_json_file(self, input_data: List[VectorInputPageContentType]):
        output_file = f"{self.source_file_path.parent}/{self.source_file_path.stem}_vectorized.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(input_data, f, indent=1, ensure_ascii=False)

    # TODO: TO TEST
    def __generate_vectorized_content(self, inputs:Dict[int, List[str]]) -> Dict[int: List[List[float]]]:
        # TODO: implement batch_size = 512
        result = {}
        for page in inputs.keys():
            contents = inputs[page]
            vectors = self.embeddings.embed_documents(contents)
            result[page] = vectors
        return result

    def __vectorize_chunks(self, chunks: Dict[int, List[str]]):
        try:
            vectorized_content = []
            dictionary_of_vectors = self.__generate_vectorized_content(chunks) # per page
            for page in dictionary_of_vectors.keys():
                vectorized_content.extend([
                    {
                        "pageContent": chunks[page][index],
                        "vectors": vector,
                        "metadata": {
                            "pageNumber": self.page if self.page != 0 else page,
                            "sourceFile": self.source_file_path.name,
                            "contentType": self.doc_type,
                            "keyWords": self.key_words,
                            "title": self.document_title
                        }
                    }
                    for index, vector in enumerate(dictionary_of_vectors[page])
                ])

            self.__save_vectorized_content_to_json_file(vectorized_content)

        except Exception as e:
            print(f"Error: {e}")