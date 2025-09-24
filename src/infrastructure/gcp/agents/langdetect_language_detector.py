from langdetect import detect, detect_langs

from domain.models import Language
from domain.logger import ContextLogger
from application.agents import LanguageDetector

class LangDetectLanguageDetector(LanguageDetector):

    def __init__(self,logger:ContextLogger):
        self.logger = logger

    def detect_lang(self, message:str) -> Language:
        # Clean the text
        message = message.strip().replace('\n', ' ')
        
        # Minimum text length check, assume French (TODO)
        if len(message) < 3:
            return Language.build_from_code("FR")
        
        try:
            # Get predictions
            language_code = detect(message)
            
            # Extract language code and confidence
            probabilities = detect_langs(message)
            confidence = next((prob.prob for prob in probabilities if prob.lang == language_code), 0.0)
            
            self.logger.debug(f"Language detection confidence: {float(confidence)}")
            return Language.build_from_code(language_code)
            
        except Exception as e:
            self.logger.error(f"Error during prediction: {e}")
            Language.build_from_code("FR")