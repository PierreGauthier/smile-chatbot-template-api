from domain.models import Language, BaseContext
from domain.fields import LanguageField
from domain.logger import ContextLogger
from domain.agents import LanguageDetector
from config import Settings

from application.prompts import StaticPromptProvider
from application.chains import BasicPydanticChain

from infrastructure.azure.ai import AzureOpenAiLlmProvider

class AzureOpenAILanguageDetector(LanguageDetector):

    def __init__(
            self,
            settings: Settings,
            prompt_provider: StaticPromptProvider,
            logger:ContextLogger):
        self.logger = logger
        self.detector_chain = BasicPydanticChain(
            settings=settings,
            llm_agent=AzureOpenAiLlmProvider(settings),
            prompt_provider=prompt_provider,
            pydantic_object=LanguageField
        )

    def detect_lang(self, message:str, context:BaseContext) -> Language:
        lang:LanguageField = self.detector_chain.invoke(user_message=message)
        return Language.build_from_code(lang.code)