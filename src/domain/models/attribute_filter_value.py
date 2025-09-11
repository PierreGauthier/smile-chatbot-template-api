from typing import Any
from dataclasses import dataclass

from domain.models import AttributeFilterDefinition

@dataclass
class AttributeFilterValue(AttributeFilterDefinition):
    value: Any # str or PriceRange