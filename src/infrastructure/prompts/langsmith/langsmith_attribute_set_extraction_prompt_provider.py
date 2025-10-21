from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from domain.models import ElasticSuiteAttributeSet

from application.prompts import AttributeSetExtractionPromptProvider

from config import Settings, get_settings

class LangsmithAttributeSetExtractionPromptProvider(AttributeSetExtractionPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_attribute_set_extraction_prompt_name

    def get_prompt(self, attribute_set:List[ElasticSuiteAttributeSet]) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)

        # Build values
        product_possible_values = "\n".join(
            f"- {attr.name}: {attr.description}" for attr in attribute_set
        )

        prompt = prompt.partial(attribute_set=product_possible_values)

        return prompt