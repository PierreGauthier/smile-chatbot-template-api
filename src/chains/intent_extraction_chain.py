from typing import Annotated
from fastapi import Depends

from config import Settings, get_settings
from services import LlmService, AzureOpenAiLlmService
from fields import IntentDefinitionField
from chains import BasicPydanticChain
from prompts import IntentExtractionPromptProvider, PromptProvider

class IntentExtractionChain(BasicPydanticChain):

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_service: Annotated[LlmService, Depends(AzureOpenAiLlmService)],
            prompt_provider: Annotated[PromptProvider, Depends(IntentExtractionPromptProvider)]):
        super().__init__(
            settings=settings,
            llm_service=llm_service,
            prompt_provider=prompt_provider,
            pydantic_object=IntentDefinitionField
        )
