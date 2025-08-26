from typing import List, Annotated
from fastapi import Depends
from config import Settings

from config import Settings, get_settings
from ai import LlmProvider
from models import ChatMessage, ProductFilterQuestion
from prompts import PromptProvider, ElasticSuiteQuestionSummarizerPromptProvider
from dependencies import inject_llm_provider

class ElasticSuiteQuestionSummarizerAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[PromptProvider, Depends(ElasticSuiteQuestionSummarizerPromptProvider)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, last_exchange: List[ChatMessage], questions: List[ProductFilterQuestion]): #TODO

        prompt_template = self.prompt_provider.get_prompt(exchange=last_exchange)
        
        new_questions = [f"- [Product: {question.attribute_set_name}] -> {question.ai_question}" for question in questions]

        new_message = '\n'.join(new_questions)
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(questions=new_message)
        output = self.llm_agent.invoke(messages)
        return output.content
