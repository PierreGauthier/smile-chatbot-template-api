from typing import List, Annotated
from fastapi import Depends
from config import Settings

from domain.ai import LlmProvider
from domain.models import ChatMessage, ProductFilterDetectionResult

from application.prompts import QuestionSummarizerPromptProvider

from dependencies import inject_deep_llm_provider, inject_question_summarizer_prompt
from config import Settings, get_settings


class QuestionsSummarizerAgent:
    """Agent that summarizes detected product questions into a single LLM prompt."""

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_deep_llm_provider)],
            prompt_provider: Annotated[QuestionSummarizerPromptProvider, Depends(inject_question_summarizer_prompt)]):
        """
        Initialize the agent with configuration, LLM gateway, and prompt templates.

        Parameters:
            settings: Application configuration injected via FastAPI.
            llm_agent: Provider responsible for invoking the LLM.
            prompt_provider: Factory for question summarization prompts.
        """
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, last_exchange: List[ChatMessage], questions: List[ProductFilterDetectionResult]):
        """
        Summarize detected product questions alongside the latest exchange context.

        Parameters:
            last_exchange: Conversation history to condition the prompt.
            questions: Structured product questions detected in the exchange.

        Returns:
            str: LLM-generated summary consolidating the product questions.
        """

        prompt_template = self.prompt_provider.get_prompt(exchange=last_exchange)
        
        new_questions = [f"- [Product: {question.attribute_set_name}] -> {question.ai_question}" for question in questions]

        new_message = '\n'.join(new_questions)
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(questions=new_message)
        output = self.llm_agent.invoke(messages)
        return output.content
