from typing import Annotated
from fastapi import Depends

from config import Settings, get_settings
from ai import LlmProvider
from fields import IntentDefinitionField
from agents import BasicPydanticChain
from prompts import IntentExtractionPromptProvider, PromptProvider
from dependencies import get_llm_agent

class IntentExtractionAgent(BasicPydanticChain):

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(get_llm_agent)],
            prompt_provider: Annotated[PromptProvider, Depends(IntentExtractionPromptProvider)]):
        super().__init__(
            settings=settings,
            llm_agent=llm_agent,
            prompt_provider=prompt_provider,
            pydantic_object=IntentDefinitionField
        )
