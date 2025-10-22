from typing import List, Annotated
from fastapi import Depends
import builtins
from functools import partial
from pydantic import ValidationError

from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from domain.ai import LlmProvider
from domain.models import AttributeFilterDto
from domain.fields import build_pydantic_model, PydanticSchema, PriceRangeField
from domain.logger import ContextLogger
from domain.tools import repair_llm_pydantic_answer

from application.prompts import FiltersExtractionPromptProvider

from dependencies import inject_llm_provider, inject_filters_extraction_prompt, inject_logger
from config import Settings, get_settings

class FilterExtractionAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_provider: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[FiltersExtractionPromptProvider, Depends(inject_filters_extraction_prompt)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="FilterExtractionAgent"))]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_provider = llm_provider
        self.logger = logger
        self.attempt = 1

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

        self.attempt = 1
        def __run_chain(exchange:str):
            self.logger.debug(f"Parsing filter extraction... attempt {self.attempt}")
            self.attempt += 1
            chain = prompt | self.llm_provider.get_llm()
            output = chain.invoke(exchange)
            repaired_json = repair_llm_pydantic_answer(json=output.content, schemas=schemas)
            response = output_parser.parse(repaired_json)
            return response
        
        runnable = RunnableLambda(__run_chain)
        response = runnable.with_retry(
            stop_after_attempt=3,
            retry_if_exception_type=(OutputParserException, ValidationError, ValueError),
        ).invoke(exchange)
        return response
