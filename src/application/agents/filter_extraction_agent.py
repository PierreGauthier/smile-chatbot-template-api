from typing import List, Annotated
from fastapi import Depends
import builtins

from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from domain.ai import LlmProvider
from domain.models import AttributeFilterDto
from domain.fields import build_pydantic_model, PydanticSchema, PriceRangeField

from application.prompts import FiltersExtractionPromptProvider

from dependencies import inject_llm_provider, inject_filters_extraction_prompt
from config import Settings, get_settings

class FilterExtractionAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_provider: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[FiltersExtractionPromptProvider, Depends(inject_filters_extraction_prompt)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_provider = llm_provider

    def invoke(self, exchange:str, filters:List[AttributeFilterDto]):
        schemas = [
            PydanticSchema(
                name=filter.code,
                required=True,
                field_type=PriceRangeField if filter.type == "price" else getattr(builtins, filter.options_type),
                description=filter.description
            )
            for filter in filters
        ]
        schemas.append(
            PydanticSchema(
                name="ai_question",
                required=True,
                field_type=str,
                description="Corresponds to the question that you will ask the user, to find out the missing fields in the final JSON response."
            )
        )
        model_type = build_pydantic_model(schemas)
        
        output_parser = PydanticOutputParser(pydantic_object=model_type)
        format_instructions = output_parser.get_format_instructions()
        prompt:ChatPromptTemplate = self.prompt_provider.get_prompt(
            filters=filters
        )
        
        prompt = prompt.partial(format_instructions=format_instructions)
        prompt.append(message=("human", "{question}"))
        chain = prompt | self.llm_provider.get_llm() | output_parser
        chain_with_retry = chain.with_retry(
            retry_if_exception_type=(ValueError, Exception),
            wait_exponential_jitter=True,
            stop_after_attempt=3
        )
        response = chain_with_retry.invoke(exchange)
        return response