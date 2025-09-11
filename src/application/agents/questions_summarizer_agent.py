from typing import List, Annotated
from fastapi import Depends
from config import Settings

from domain.ai import LlmProvider
from domain.models import ChatMessage, ProductFilterDetectionResult

from application.prompts import QuestionSummarizerPromptProvider

from dependencies import inject_llm_provider, inject_question_summarizer_prompt
from config import Settings, get_settings

class QuestionsSummarizerAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[QuestionSummarizerPromptProvider, Depends(inject_question_summarizer_prompt)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, last_exchange: List[ChatMessage], questions: List[ProductFilterDetectionResult]): #TODO

        prompt_template = self.prompt_provider.get_prompt(exchange=last_exchange)
        
        new_questions = [f"- [Product: {question.attribute_set_name}] -> {question.ai_question}" for question in questions]

        new_message = '\n'.join(new_questions)
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(questions=new_message)
        output = self.llm_agent.invoke(messages)
        return output.content
