from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from domain.models import ElasticSuiteAttributeSet

from application.prompts import AttributeSetExtractionPromptProvider

from config import Settings, get_settings

class LangsmithAttributeSetExtractionPromptProvider(AttributeSetExtractionPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.prompt_name = settings.langsmith_attribute_set_extraction_prompt_name

    def get_prompt(self, attribute_set:List[ElasticSuiteAttributeSet], product_counter_example:str) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = hub.pull(self.prompt_name)

        # Build values
        product_possible_values = "\n".join(
            f"- {attr.name}: {attr.description}" for attr in attribute_set
        )
        example1_name = attribute_set[0].name.capitalize()
        example1_value = attribute_set[0].name.lower()

        example2_name = attribute_set[1].name.capitalize()
        example2_value = attribute_set[1].name.lower()

        prompt = prompt.partial(
            attribute_set=product_possible_values,
            attribute_example1_name=example1_name,
            attribute_example1_value=example1_value,
            attribute_example2_name=example2_name,
            attribute_example2_value=example2_value,
            attribute_counter_example=product_counter_example,
        )

        return prompt