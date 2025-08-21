from typing import List, Annotated
from fastapi import Depends
from config import Settings

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import Settings, get_settings
from ai import LlmProvider
from models import AttributeFilterDto, PydanticSchema
from prompts import PromptProvider, FiltersExtractionPromptProvider
from dependencies import inject_llm_provider
from fields import build_pydantic_model

class FilterExtractionAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[PromptProvider, Depends(FiltersExtractionPromptProvider)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent

    def invoke(self, exchange:str, filters:List[AttributeFilterDto]):
        schemas = [
            PydanticSchema(
                name=filter.code,
                required=True,
                type=filter.type,
                description=filter.description
            )
            for filter in filters
        ]
        schemas.append(
            PydanticSchema(
                name="ai_question",
                required=True,
                type="str",
                description="Corresponds to the question that you will ask the user, to find out the missing fields in the final JSON response."
            )
        )
        model_type = build_pydantic_model(schemas)
        
        output_parser = PydanticOutputParser(pydantic_object=model_type)
        format_instructions = output_parser.get_format_instructions()
        prompt_template:ChatPromptTemplate = self.prompt_provider.get_prompt(
            filters=filters
        )

        prompt_template.append(message=("human", "{question}"))
        messages = prompt_template.format_messages(question=exchange, format_instructions=format_instructions)
        output = self.llm_agent.invoke(messages)

        response = output_parser.parse(output.content)
        return response