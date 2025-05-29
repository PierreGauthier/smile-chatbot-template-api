from chunking import CsvFileVectoriser

class FAQ_Vectorized(CsvFileVectoriser):
    def __init__(self, page:int, source_filename:str):
        super().__init__(
            source_filename=source_filename, 
            document_title="Frequently Asked Questions",
            key_words=["questions", "FAQ"],
            doc_type="FAQ",
            page=page
        )

    def build_line(self, row:list[str]):
        return f"One posible answer for the question \"{row[0]}\", could be the following: {row[1]}"