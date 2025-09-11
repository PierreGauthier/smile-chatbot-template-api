from dataclasses import dataclass

@dataclass
class Source:
    name: str
    type: str
    page_number: int
    address: str