from typing import Annotated, List
from fastapi import Depends

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import Settings, get_settings
from ai import LlmProvider
from fields import AttributeField
from prompts import AttributeSetExtractionPromptProvider, PromptProvider
from dependencies import inject_llm_provider
from models import ElasticSuiteAttributeSet

class AttributeSetExtractionAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[PromptProvider, Depends(AttributeSetExtractionPromptProvider)]):
        self.settings = settings
        self.llm_agent = llm_agent
        self.prompt_provider = prompt_provider
        self.pydantic_object = AttributeField

    def invoke(self, user_message: str, attribute_set:List[ElasticSuiteAttributeSet], product_counter_example:str):
        output_parser = PydanticOutputParser(pydantic_object=self.pydantic_object)
        format_instructions = output_parser.get_format_instructions()
        prompt_template:ChatPromptTemplate = self.prompt_provider.get_prompt(
            attribute_set=attribute_set, 
            product_counter_example=product_counter_example
        )

        prompt_template.append(message=("human", "{question}"))
        messages = prompt_template.format_messages(question=user_message, format_instructions=format_instructions)
        output = self.llm_agent.invoke(messages)

        response = output_parser.parse(output.content)
        return response
