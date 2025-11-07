from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from domain.models import ElasticSuiteAttributeSet, SearchContext

from application.prompts import PromptProvider

from config import Settings, get_settings

class LangsmithAttributeSetExtractionPromptProvider(PromptProvider[SearchContext]):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_attribute_set_extraction_prompt_name

    def get_prompt(self, context:SearchContext) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)

        attribute_set = [
            ElasticSuiteAttributeSet(name=attr.code, description=attr.description) 
            for attr in context.attribute_sets
        ]
        # Build values
        product_possible_values = "\n".join(
            f"- {attr.name}: {attr.description}" for attr in attribute_set
        )

        prompt = prompt.partial(attribute_set=product_possible_values)

        return prompt