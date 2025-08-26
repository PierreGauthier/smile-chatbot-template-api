from dataclasses import dataclass

@dataclass
class ProductFilterQuestion:
    attribute_set_name:str
    ai_question:str