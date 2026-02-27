from typing import Annotated
from fastapi import Depends

from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from domain.models import SearchContext
from domain.ai import LlmProvider
from domain.fields import SearchTermField

from application.prompts import PromptProvider

from dependencies import inject_deep_llm_provider, inject_search_term_extraction_prompt
from config import Settings, get_settings

class SearchTermExtractionAgent:
    """Extract the main search term from a user message, independent of attribute sets."""

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_deep_llm_provider)],
            prompt_provider: Annotated[PromptProvider[SearchContext], Depends(inject_search_term_extraction_prompt)]):
        """Store injected dependencies for search term extraction."""
        self.settings = settings
        self.llm_agent = llm_agent
        self.prompt_provider = prompt_provider
        self.pydantic_object = SearchTermField

    def invoke(self, context: SearchContext) -> str:
        """Extract and return the search term from the user's message."""
        output_parser = PydanticOutputParser(pydantic_object=self.pydantic_object)
        format_instructions = output_parser.get_format_instructions()
        prompt_template: ChatPromptTemplate = self.prompt_provider.get_prompt(context)

        prompt_template = prompt_template.partial(format_instructions=format_instructions)
        messages = prompt_template.format_messages(question=context.exchange)
        output = self.llm_agent.invoke(messages)

        response = output_parser.parse(output.content)
        return response.term