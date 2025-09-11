from typing import List
from dataclasses import dataclass

from domain.models import AttributeFilterValue

@dataclass
class ProductFilterDetectionResult:
    attribute_set_name:str
    attribute_set_id:int
    ai_question:str
    detected_filters:List[AttributeFilterValue]