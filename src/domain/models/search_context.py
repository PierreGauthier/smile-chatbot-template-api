from typing import List
from dataclasses import dataclass, field

from domain.fields import AttributeField
from domain.models import (
    ChatMessage,
    UserRequestDto,
    AttributeSetDto,
    ProductFilterDetectionResult,
    SearchResponseItem
)

@dataclass
class SearchContext:
    input_message: str
    user_id: str
    session_id:str
    is_first_call:bool
    message_thread: List[ChatMessage] = field(default_factory=list)
    exchange: str = ""
    requests: List[UserRequestDto] = field(default_factory=list)
    attribute_sets: List[AttributeSetDto] = field(default_factory=list)
    detected_attribute_sets: AttributeField = None
    request_chain_results: List[ProductFilterDetectionResult] = field(default_factory=list)
    ai_answer:str = ""
    search_result:List[SearchResponseItem] = field(default_factory=list)