from dataclasses import dataclass

@dataclass
class Source:
    name: str
    type: str
    page_number: int
    address: str

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "page_number": self.page_number,
            "address": self.address
        }