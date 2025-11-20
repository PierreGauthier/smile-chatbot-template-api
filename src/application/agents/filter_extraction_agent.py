from typing import List, Annotated
from fastapi import Depends
import builtins
from pydantic import ValidationError

from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from domain.ai import LlmProvider
from domain.models import AttributeFilterDto, SearchContext
from domain.fields import build_pydantic_model, PydanticSchema, PriceRangeField
from domain.logger import ContextLogger
from domain.tools import repair_llm_pydantic_answer

from application.prompts import PromptProvider

from dependencies import inject_deep_llm_provider, inject_filters_extraction_prompt, inject_logger
from config import Settings, get_settings

class FilterExtractionAgent:
    """Coordinate prompt-driven LLM calls to extract structured attribute filters from dialogues."""

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_provider: Annotated[LlmProvider, Depends(inject_deep_llm_provider)],
            prompt_provider: Annotated[PromptProvider[SearchContext], Depends(inject_filters_extraction_prompt)],
            logger: Annotated[ContextLogger, Depends(inject_logger)]):
        """Store injected dependencies used to generate prompts, call the LLM, and log attempts."""
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_provider = llm_provider
        self.logger = logger
        self.attempt = 1

    def invoke(self, context:SearchContext):
        """Parse user input into a validated filter payload using retryable LLM invocations."""
        attribute_set = next((attr for attr in context.attribute_sets if attr.code == context.detected_attribute_set.product), None)
        filters:List[AttributeFilterDto] = attribute_set.filters
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
        prompt:ChatPromptTemplate = self.prompt_provider.get_prompt(context)
        prompt = prompt.partial(format_instructions=format_instructions)
        prompt.append(message=("human", "{question}"))

        self.attempt = 1
        def __run_chain(exchange:str):
            self.logger.debug_context(f"Parsing filter extraction... attempt {self.attempt}", context)
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
        ).invoke(context.exchange)
        return response
