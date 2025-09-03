from typing import Annotated
from fastapi import Depends

from config import Settings, get_settings
from ai import LlmProvider
from fields import IntentDefinitionField
from agents import BasicPydanticChain
from prompts import StaticPromptProvider
from dependencies import inject_llm_provider, inject_intent_extraction_prompt

class IntentExtractionAgent(BasicPydanticChain):

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[StaticPromptProvider, Depends(inject_intent_extraction_prompt)]):
        super().__init__(
            settings=settings,
            llm_agent=llm_agent,
            prompt_provider=prompt_provider,
            pydantic_object=IntentDefinitionField
        )
