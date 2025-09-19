from dataclasses import dataclass

@dataclass
class SearchResponseItem:
    id:int
    sku:str
    name:str
    price:str
    image_url:str