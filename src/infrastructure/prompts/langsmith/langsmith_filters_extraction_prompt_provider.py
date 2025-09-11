from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from domain.models import AttributeFilterDto

from application.prompts import FiltersExtractionPromptProvider

from config import Settings, get_settings

class LangsmithFiltersExtractionPromptProvider(FiltersExtractionPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.prompt_name = settings.langsmith_filters_extraction_prompt_name

    def get_prompt(self, filters:List[AttributeFilterDto]) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = hub.pull(self.prompt_name)

        param_filters = "\n".join(
            f"- **{filter.code}**: {filter.description or self._build_description(filter.code)}" 
            for filter in filters
        )
        param_filter_list = self._get_filter_list(len(filters), filters)
        param_three_not_yet_found_filters = self._get_filter_list(3, filters)
        param_two_not_yet_found_filters = self._get_filter_list(2, filters)
        param_one_not_yet_found_filter = f"`{filters[2]}`"

        prompt = prompt.partial(
            filters=param_filters,
            filter_list=param_filter_list,
            three_not_yet_found_filters=param_three_not_yet_found_filters,
            two_not_yet_found_filters=param_two_not_yet_found_filters,
            one_not_yet_found_filter=param_one_not_yet_found_filter
        )

        return prompt
    
    def _build_description(self, code:str):
        return f"The {code} of the product."
    
    def _get_filter_list(self, n:int, filters:List[AttributeFilterDto]):
        return ", ".join(f"`{filter.code}`" for filter in filters[:n])