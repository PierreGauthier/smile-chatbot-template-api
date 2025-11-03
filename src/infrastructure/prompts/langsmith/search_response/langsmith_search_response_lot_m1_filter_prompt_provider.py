from typing import Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from domain.models import SearchContext
from application.prompts import RagMainPromptProvider

from config import Settings, get_settings

class LangsmithSearchResponseLotM1FilterPromptProvider(RagMainPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.elastic_suite_search_response_lot_m1_filter

    def get_prompt(self, search_context:SearchContext) -> ChatPromptTemplate:
        
        rag_prompt:ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)
        nb_product_show = 5
        product_list_show = '\n'.join([
            f"* {item.name} - {item.price}" 
            for item in search_context.search_result[:nb_product_show]
        ])
        all_filters = "\n".join([
            f"- {f.label}"
            for f in search_context.attribute_sets[0].filters
        ])
        detected_filters = "\n".join([
            f"- {f.label}: {f.value}"
            for f in search_context.get_valued_filters()
        ])
        used_codes = {f.code for f in search_context.search_used_filters}
        unused_filters = [f for f in search_context.get_valued_filters() if f.code not in used_codes]
        rag_prompt = rag_prompt.partial(
            product_name=search_context.detected_attribute_sets.terms[0],
            nb_products=search_context.search_total_count, 
            nb_product_show=nb_product_show,
            product_list_show=product_list_show,
            all_filters=all_filters,
            detected_filters=detected_filters,
            removed_filter=unused_filters[0].label,
            lang=search_context.search_lang
        )

        return rag_prompt