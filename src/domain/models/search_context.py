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
    BaseContext
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
    ai_answer:str = ""
    search_result:List[SearchResponseItem] = field(default_factory=list)