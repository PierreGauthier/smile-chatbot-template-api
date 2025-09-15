from typing import Annotated
from fastapi import Depends

from domain.ai import LlmProvider
from domain.models import UserRequestDto, SearchResponseItem

# Avoid circular dependency injection
from application.agents.search_response_builder_agent import SearchResponseBuilderAgent

from application.prompts import StaticPromptProvider
from config import Settings, get_settings

class ElasticSuiteSearchResponseBuilderAgent(SearchResponseBuilderAgent):

    def __init__(self, 
            settings: Settings, 
            llm_provider: LlmProvider,
            empty_search_prompt_provider: StaticPromptProvider,
            not_empty_search_prompt_provider: StaticPromptProvider):
        super().__init__(settings, llm_provider, empty_search_prompt_provider, not_empty_search_prompt_provider)

    def build_filter_value(self, request:UserRequestDto, filter:str):
        if filter == "price":
            min_price = request.data[filter]["min_price"]
            max_price = request.data[filter]["max_price"]
            return f"{min_price}-{max_price}"
        else:
            return request.data[filter]

    def build_product(self, product:SearchResponseItem):
        return f"{product.name} - {product.brand_name} - {product.price}"