from typing import Annotated
from fastapi import Depends

from domain.ai import LlmProvider
from domain.fields import IntentDefinitionField

from application.chains import BasicPydanticChain
from application.prompts import StaticPromptProvider

from dependencies import inject_llm_provider, inject_intent_extraction_prompt
from config import Settings, get_settings
class IntentExtractionAgent(BasicPydanticChain):
    """Chain wrapper that extracts intent metadata using the configured LLM and prompt."""

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[StaticPromptProvider, Depends(inject_intent_extraction_prompt)]):
        """Build the intent extraction chain with injected dependencies."""
        super().__init__(
            settings=settings,
            llm_agent=llm_agent,
            prompt_provider=prompt_provider,
            pydantic_object=IntentDefinitionField
        )
