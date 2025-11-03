from typing import List
from dataclasses import dataclass, field

from domain.fields import AttributeField
from domain.models import (
    ChatMessage,
    UserRequestDto,
    AttributeSetDto,
    ProductFilterDetectionResult,
    SearchResponseItem,
    Language,
    BaseContext,
    AttributeFilterValue
)

@dataclass
class SearchContext(BaseContext):
    input_message: str
    is_first_call:bool
    search_lang:Language = None
    chat_lang:Language = None
    message_thread: List[ChatMessage] = field(default_factory=list)
    exchange: str = ""
    requests: List[UserRequestDto] = field(default_factory=list)
    attribute_sets: List[AttributeSetDto] = field(default_factory=list)
    detected_attribute_sets: AttributeField = None
    request_chain_results: List[ProductFilterDetectionResult] = field(default_factory=list)
    search_used_filters: List[AttributeFilterValue] = field(default_factory=list)
    ai_answer:str = ""
    search_result:List[SearchResponseItem] = field(default_factory=list)
    search_total_count:int = 0

    def get_valued_filters(self):
        return [f for f in self.request_chain_results[0].detected_filters if self.__is_valued(f.value)]
    
    def __is_valued(self, filter_value):
        if isinstance(filter_value, dict):
            # handle case where PriceRangeField is represented as dict
            min_price = filter_value.get("min_price") or 0
            max_price = filter_value.get("max_price") or 0
            return max_price > 0 or min_price > 0
        else:
            return True if filter_value else False