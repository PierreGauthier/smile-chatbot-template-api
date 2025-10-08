from typing import Annotated
from fastapi import Depends
from functools import partial

from domain.models import SearchContext, Language
from domain.logger import ContextLogger

from domain.agents import LanguageDetector

from config import Settings, get_settings
from dependencies import inject_language_detector, inject_logger

class LanguageManager:

    def __init__(
            self, 
            settings: Annotated[Settings, Depends(get_settings)],
            language_detector: Annotated[LanguageDetector, Depends(inject_language_detector)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="LanguageManager"))]):
        self.language_detector = language_detector
        self.settings = settings
        self.logger = logger

    def configure_languages(self, input_message:str, context:SearchContext) -> SearchContext:
        search_language:Language = Language.build_from_code(self.settings.search_lang)
        chat_language:Language = self.language_detector.detect_lang(message=input_message)
        context.search_lang = search_language
        context.chat_lang = chat_language
        return context