from dataclasses import dataclass
from typing import List

@dataclass
class ElasticSuiteAnswer:
    message: str
    products: List [dict] 