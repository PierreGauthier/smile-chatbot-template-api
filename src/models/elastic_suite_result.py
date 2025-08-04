from dataclasses import dataclass
from typing import List

from models import ElasticSuiteAnswer

@dataclass
class ElasticSuiteResult:
    user_id:str
    session_id:str
    messages: List[ElasticSuiteAnswer]