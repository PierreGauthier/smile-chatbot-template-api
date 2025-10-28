from domain.models import Language, BaseContext
from domain.fields import LanguageField
from domain.logger import ContextLogger
from domain.agents import LanguageDetector
from config import Settings

from application.chains import BasicPydanticChain

from infrastructure.azure.ai import AzureOpenAiLlmProvider
from infrastructure.prompts.langsmith import LangsmithLanguageDetectorPromptProvider

class AzureOpenAILanguageDetector(LanguageDetector):

    def __init__(
            self,
            settings: Settings,
            logger:ContextLogger):
        self.logger = logger
        self.detector_chain = BasicPydanticChain(
            settings=settings,
            llm_agent=AzureOpenAiLlmProvider(settings),
            prompt_provider=LangsmithLanguageDetectorPromptProvider(settings),
            pydantic_object=LanguageField
        )

    def detect_lang(self, message:str, context:BaseContext) -> Language:
        lang:LanguageField = self.detector_chain.invoke(user_message=message)
        return Language.build_from_code(lang.code)