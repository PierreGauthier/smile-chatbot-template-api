from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from domain.models import AttributeFilterDto, SearchContext
from application.prompts import PromptProvider

from config import Settings, get_settings

class LangsmithFiltersExtractionPromptProvider(PromptProvider[SearchContext]):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_filters_extraction_prompt_name

    def get_prompt(self, context:SearchContext) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)

        attribute_set = next((attr for attr in context.attribute_sets if attr.code == context.detected_attribute_set.product), None)
        filters:List[AttributeFilterDto] = attribute_set.filters

        filters_declarations = []
        for filter in filters:
            data_type_str = ""
            if filter.type == "price":
                if filter.options_type  == "str":
                    data_type_str = " (data-type = string)"
                elif filter.options_type  == "int":
                    data_type_str = " (data-type = integer)"           
            filters_declarations.append(f"- **{filter.code}**: {filter.description or self._build_description(filter.type, filter.label.lower())}{data_type_str}")
            
        param_filters = "\n".join(filters_declarations)

        filter_options_items = []
        for filter in filters:
            if filter.type == "price":
                if filter.options and len(filter.options) == 2:
                    filter_options = f"between {filter.options[0]} and {filter.options[1]}"
                else:
                    continue
            else:
                filter_options = ", ".join(str(option) for option in filter.options)
            filter_options_items.append(f"- **{filter.code}**: {filter_options}")
        param_filters_options = "\n".join(filter_options_items)

        param_filter_list = self._get_filter_list(len(filters), filters)
        param_three_not_yet_found_filters = self._get_filter_list(3, filters)
        param_two_not_yet_found_filters = self._get_filter_list(2, filters)
        param_one_not_yet_found_filter = f"`{filters[2]}`"

        prompt = prompt.partial(
            filters=param_filters,
            filter_list=param_filter_list,
            filter_possible_values=param_filters_options,
            three_not_yet_found_filters=param_three_not_yet_found_filters,
            two_not_yet_found_filters=param_two_not_yet_found_filters,
            one_not_yet_found_filter=param_one_not_yet_found_filter
        )

        return prompt
    
    def _build_description(self, type:str, value:str):
        if type == "price":
            return f"The {value} of the product. In this case, here is a price range logic (interpret common phrasing): \n\t- `budget of X`, `up to X`, `at most X`, `no more than X`, `under/less than X` → min_price = 0, max_price = X\n\t- `between X and Y`, `X-Y`, `from X to Y` → min_price = min(X, Y), max_price = max(X, Y)."
        return f"The {value} of the product."
    
    def _get_filter_list(self, n:int, filters:List[AttributeFilterDto]):
        return ", ".join(f"`{filter.code}`" for filter in filters[:n])